from machine import Pin, Timer
import xpt2046
import micropython

bl_timer = Timer(1)
xpt = None
spi = None
backlight = None


def lightup():
    backlight.duty(0)
    bl_timer.init(
        period=5000,
        mode=Timer.ONE_SHOT,
        callback=lambda timer: micropython.schedule(lightdown, timer)
        )
    return


def lightdown(timer):
    backlight.duty(900)
    return


def init(_backlight, _spi):
    print("initializing backlight interrupt...")
    global xpt, backlight, spi
    backlight = _backlight
    spi = _spi
    lightup()
    xpt = xpt2046.Touch(spi, cs=Pin(14), int_pin=Pin(27), int_handler=lambda x, y: lightup())
    return
