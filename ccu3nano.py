# initialize display
from gui.core.nanogui import refresh, fillcircle
from gui.core.writer import CWriter
from gui.core.colors import *
from gui.widgets.label import Label
import gui.fonts.font6 as font
# initialize all the rest
import urequests
import ujson
import time
from machine import Timer, reset
import micropython
import gc

wri = None
ssd = None

PALE_RED = create_color(12, 255, 192, 192)
PALE_GREEN = create_color(13, 192, 255, 192)
DARK_GREY = create_color(14, 64, 64, 64)

config_data = {}
room_data = {
    "rooms":  []
    }

request_timer = Timer(0)

login_string = '{{"jsonrpc": "1.1", "id": 0, "method": "Session.login", "params": {{"username":"{0}", "password":"{1}"}}}}'
logout_string = '{{"jsonrpc": "1.1", "id": 0, "method": "Session.logout", "params": {{"_session_id_":"{0}"}}}}'
getall_string = '{{"jsonrpc": "1.1", "id": 0, "method": "SysVar.getAll", "params": {{"_session_id_":"{0}"}}}}'

_session_id = ""
_logging = False
_errorCounter = 0


def init(_ssd):
    print("initializing ccu3...")
    global wri, ssd
    ssd = _ssd
    CWriter.set_textpos(ssd, 0, 0)
    wri = CWriter(ssd, font, WHITE, BLACK, verbose=False)
    wri.set_clip(True, True, False)
    load_config()
    ssd.fill(BLACK)
    ssd.rect(0, 0, ssd.width - 1, ssd.height - 1, WHITE)
    fillcircle(ssd, 309, 229, 5, WHITE)
    fillcircle(ssd, 309, 229, 4, BLACK)
    refresh(ssd)
    repaint_data()
    return


def load_config(path="config/ccu3_config.json"):
    global config_data, room_data
    try:
        with open(path) as file:
            config_data = ujson.load(file)
            print("room count: {0}".format(len(config_data['variables'])))
            room_data['rooms'].clear()
            for room_number in range(len(config_data['variables'])):
                new_room = {"name": config_data['variables'][room_number]['name'], "id": config_data['variables'][room_number]['id'], "state": True}
                room_data['rooms'].append(new_room)
    except Exception as ex:
        print("error on reading config file: " + str(ex))
        return False
    return True


def handle_error():
    global _errorCounter
    if config_data['rebootAfterErrors'] > 0:
        _errorCounter = _errorCounter + 1
        print("counting {0} of {1} errors before reboot".format(_errorCounter, config_data['rebootAfterErrors']))
        if _errorCounter >= config_data['rebootAfterErrors']:
            reset()
    return


def login():
    global _session_id, _errorCounter
    if _logging:
        print("Request: {0}".format(login_string.format(config_data['username'], config_data['password'])))
    start_time = time.ticks_ms()
    try:
        response_login = urequests.request('POST', config_data['url'], login_string.format(config_data['username'], config_data['password']))
        stop_time = time.ticks_ms()
        duration = time.ticks_diff(stop_time, start_time)
        if _logging:
            print("Response: {0}".format(response_login.text))
            print("Duration: {0} ms".format(duration))
        response_login_object = ujson.loads(response_login.text)
        _session_id = response_login_object['result']
        _errorCounter = 0
    except Exception as ex:
        print("error on api call: " + str(ex))
        handle_error()
        _session_id = ""
    return


def logout():
    global _session_id
    result = True
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(logout_string.format(_session_id)))
        start_time = time.ticks_ms()
        try:
            response_logout = urequests.request('POST', config_data['url'], logout_string.format(_session_id))
            stop_time = time.ticks_ms()
            duration = time.ticks_diff(stop_time, start_time)
            if _logging:
                print("Response: {0}".format(response_logout.text))
                print("Duration: {0} ms".format(duration))
            response_logout_object = ujson.loads(response_logout.text)
            result = response_logout_object['result']
            if result:
                _session_id = ""
        except Exception as ex:
            print("error on api call: " + str(ex))
            handle_error()
            _session_id = ""
    else:
        print("warning: no session")
    return


def get_all():
    global _session_id
    response_getall_object = None
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(getall_string.format(_session_id)))
        start_time = time.ticks_ms()
        try:
            response_getall = urequests.request('POST', config_data['url'], getall_string.format(_session_id))
            stop_time = time.ticks_ms()
            duration = time.ticks_diff(stop_time, start_time)
            if _logging:
                print("Duration: {0} ms".format(duration))
            response_getall_object = ujson.loads(response_getall.text)
        except Exception as ex:
            print("error on api call: " + str(ex))
            handle_error()
            _session_id = ""
    else:
        print("warning: no session")
        login()
    return response_getall_object


def timer_callback(timer):
    global room_data
    gc.collect()
    
    fillcircle(ssd, 309, 229, 5, WHITE)
    refresh(ssd)
    
    error_state = False
    error_message = ""
    
    # get data
    response_getall_object = get_all()
    if response_getall_object is not None:
        if response_getall_object['result'] is not None:
            for room in room_data['rooms']:
                for result in response_getall_object['result']:
                    if result['id'] == room['id']:
                        room['state'] = (result['value'] == 'true')
                        break
        if response_getall_object['error'] is not None:
            error_state = True
            error_message = response_getall_object['error']['message']
    else:
        error_state = True
            
    # draw error state as border
    if error_state:
        fillcircle(ssd, 309, 229, 4, RED)
    else:
        fillcircle(ssd, 309, 229, 4, GREEN)
    refresh(ssd)
    
    repaint_data()
    
    # relogin on error
    if error_state:
        logout()
        login()
    return


def repaint_data():
    for room_number in range(len(room_data['rooms'])):
        if room_data['rooms'][room_number]['state']:
            ssd.fill_rect(19 + ((room_number // 8) * 150), 24 * ((room_number % 8) + 1), 130, 22, GREEN)
            ssd.rect(19 + ((room_number // 8) * 150), 24 * ((room_number % 8) + 1), 130, 22, PALE_GREEN)
            Label(wri, 24 * ((room_number % 8) + 1) + 5, 24 + ((room_number // 8) * 150) , room_data['rooms'][room_number]['name'], invert=False, fgcolor=BLACK, bgcolor=GREEN, bdcolor=False)
        else:
            ssd.fill_rect(19 + ((room_number // 8) * 150), 24 * ((room_number % 8) + 1), 130, 22, RED)
            ssd.rect(19 + ((room_number // 8) * 150), 24 * ((room_number % 8) + 1), 130, 22, PALE_RED)
            Label(wri, 24 * ((room_number % 8) + 1) + 5, 24 + ((room_number // 8) * 150), room_data['rooms'][room_number]['name'], invert=False, fgcolor=BLACK, bgcolor=RED, bdcolor=False)
    refresh(ssd)
    return


def start_timer(logging=False):
    print("initializing ccu3 connection...")
    global _logging
    _logging = logging
    login()
    config_period = max(config_data['period'], 5000)
    print("setting timer to {0} ms period".format(config_period))
    request_timer.init(
        period=config_period,
        mode=Timer.PERIODIC,
        callback=lambda timer: micropython.schedule(timer_callback, timer)
    )
    return
    
    
def stop_timer():
    request_timer.deinit()
    logout()
    return
