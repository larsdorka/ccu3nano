import gc
print("")

from color_setup import ssd, backlight, spi

gc.collect()

import modules.wifi as wifi

wifi.load_config()
wifi.connect_scan()

gc.collect()

import ccu3nano
ccu3nano.init(ssd)
import touchBL
touchBL.init(backlight, spi)

gc.collect()

ccu3nano.start_timer(logging=True)

print("application initialized")
print("")
