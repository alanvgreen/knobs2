# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021-2024 Peter Hinch

# With modifications

# This file defines globals specifying the hardware configuration
# it should be imported early in the initialization.

from machine import Pin, SoftSPI, SPI, freq
import gc

# from drivers.ili93xx.ili9341 import ILI9341 as SSD
from drivers.ili93xx.ili9341_2 import ILI9341_2 as SSD

freq(250_000_000)  # RP2 overclock
# Create and export an SSD instance
prst = Pin(21, Pin.OUT, value=1)
pdc = Pin(20, Pin.OUT, value=0)  # Arbitrary pins
pcs = Pin(17, Pin.OUT, value=1)
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16), baudrate=30_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, height=320, width=240, usd=True)  # 320h x 240w
# ssd = SSD(spi, pcs, pdc, prst, height=240, width=320, usd=False)  # 240x320 default

from gui.core.tgui import Display  # noqa: E402

# from gui.core.tgui import quiet # noqa: E402
# quiet()  # Comment this out for periodic free RAM messages

# Touch configuration
from touch.xpt2046 import XPT2046  # noqa: E402

spi = SoftSPI(mosi=Pin(15), miso=Pin(12), sck=Pin(14))  # 2.5MHz max
tpad = XPT2046(spi, Pin(13), ssd)
# To create a tpad.init line for your displays please read SETUP.md
tpad.init(240, 320, 116, 349, 4095, 3962, False, True, False)  # portrait
# tpad.init(240, 320, 35, 328, 4095, 4000, True, False, False) #landscape

display = Display(ssd, tpad)
