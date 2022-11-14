from machine import Pin, SPI, PWM
import gc

from drivers.ili93xx.ili9341 import ILI9341 as SSD
from gui.core.nanogui import refresh 

print("initializing display...")

pdc = Pin(4, Pin.OUT, value=0)
pcs = Pin(5, Pin.OUT, value=1)
prst = Pin(22, Pin.OUT, value=1)

gc.collect()  # Precaution before instantiating framebuf
spi = SPI(2, 10_000_000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
ssd = SSD(spi, dc=pdc, cs=pcs, rst=prst)

refresh(ssd, True)

backlight = PWM(Pin(15))
backlight.duty(1000)

print("")
