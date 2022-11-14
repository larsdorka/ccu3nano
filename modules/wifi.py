import network
import ujson
import time

config_file_path = ""
filedata = {}
configCount = 0
_ssid = ""
_wpa = ""
_wlan = network.WLAN(network.STA_IF)
_wlan.active(True)


def load_config(path="config/wlan.json"):
    print("initializing wifi...")
    global config_file_path, filedata, configCount 
    config_file_path = path
    try:
        with open(config_file_path) as file:
            filedata = ujson.load(file)
    except Exception as ex:
        print("error on reading config file: " + str(ex))
    configCount = min(len(filedata['ssid']), len(filedata['wpa']))
    print("found {0} configs".format(configCount))


def connect_scan(timeout=10):
    global _ssid, _wpa
    if configCount > 0:
        print("scanning...")
        wifis = _wlan.scan()
        wifi_ssids = []
        for entry in wifis:
            wifi_ssids.append(entry[0].decode('ASCII'))
        if len(wifi_ssids) > 0:
            for j in range(len(wifi_ssids)):
                for i in range(configCount):
                    _ssid = filedata['ssid'][i]
                    _wpa = filedata['wpa'][i]
                    if wifi_ssids[j] == _ssid:
                        startTime = time.ticks_ms()
                        _wlan.connect(_ssid, _wpa)
                        while not _wlan.isconnected() and time.ticks_diff(time.ticks_ms(), startTime) < timeout * 1000:
                            print("connecting to {0}...".format(_ssid))
                            time.sleep_ms(1000)
                        if _wlan.isconnected():
                            print("connected!")
                            print(_wlan.ifconfig()[0])
                            print("")
                            return
                        else:
                            print("could not connect")
                            _wlan.disconnect()
        else:
            print("warning: no ssids found")
    else:
        print("warning: no configs loaded")
    print("")
    return


def connect_all(timeout=10):
    global _ssid, _wpa
    if configCount > 0:
        for i in range(configCount):
            _ssid = filedata['ssid'][i]
            _wpa = filedata['wpa'][i] 
            start_time = time.ticks_ms()
            _wlan.connect(_ssid, _wpa)
            while not _wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start_time) < timeout * 1000:
                print("connecting to {0}...".format(_ssid))
                time.sleep_ms(1000)
            if _wlan.isconnected():
                print("connected!")
                print(_wlan.ifconfig()[0])
                break
            else:
                print("could not connect")
                _wlan.disconnect()
    else:
        print("warning: no configs loaded")
    print("")
    return


def disconnect():
    if _wlan.isconnected():
        _wlan.disconnect()
    return
