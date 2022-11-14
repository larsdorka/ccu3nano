import gc
print("")

from color_setup import ssd, backlight, spi
import modules.wifi as wifi

wifi.load_config()
wifi.connect_scan()

gc.collect()

import ccu3nano
ccu3nano.init(ssd)
import touchBL
touchBL.init(backlight, spi)
ccu3nano.start_timer(logging=False)

print("application initialized")
print("")
