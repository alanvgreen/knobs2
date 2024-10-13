# ILI9341 nano-gui driver for ili9341 displays
# As with all nano-gui displays, touch is not supported.

# Copyright (c) Peter Hinch 2020
# Released under the MIT license see LICENSE

# This work is based on the following sources.
# https://github.com/rdagger/micropython-ili9341
# Also this forum thread with ideas from @minyiky:
# https://forum.micropython.org/viewtopic.php?f=18&t=9368

from . import ili9341

import asyncio
import time
import _thread
from clut_pio import ClutPio, DmaMemClut, DmaClutSpi, DmaSpiNull


FRAMES = 300
class RateWatcher:
    """Shows FPS over some number of frames"""
    def __init__(self):
        self.c = 0
        self.t = time.ticks_ms()

    def tick(self):
        self.c += 1
        if self.c < FRAMES:
            return
        now = time.ticks_ms()
        hz = (FRAMES * 1000) // (now - self.t)
        print(f"{hz} fps")
        self.c = 0
        self.t = now

            

class Stamper:
    def __init__(self):
        self.s = []
        self.c = 0

    def begin(self):
        self.s = self.s[-5:]
        self.c += 1
        self.s.append([])
        self.stamp()

    def stamp(self):
        self.s[-1].append(time.ticks_ms())

    def end(self):
        self.stamp()
        if self.c == 60:
            for row in self.s:
                print(', '.join(str(t) for t in row))


class ILI9341_3(ili9341.ILI9341):
    def __init__(self, spi, *args, **kwargs):
        super().__init__(spi, *args, **kwargs)
        self._do_refresh_done = False
        self._clut = ClutPio()
        self._dma_in = DmaMemClut(self._mvb, self._clut)
        self._dma_out = DmaClutSpi(self._clut, self._spi, len(self._mvb) * 4)
        self._dma_null = DmaSpiNull(self._spi, len(self._mvb) * 4)
        self._watcher = RateWatcher()
        self._stamper = Stamper()

    def show(self):
        self._watcher.tick()
        self._stamper.begin()
        ht = self.height
        if self._spi_init:  # A callback was passed
            self._spi_init(self._spi)  # Bus may be shared
        # Commands needed to start data write
        self._wcd(b"\x2a", int.to_bytes(self.width, 4, "big"))  # SET_COLUMN
        self._wcd(b"\x2b", int.to_bytes(ht, 4, "big"))  # SET_PAGE
        self._wcmd(b"\x2c")  # WRITE_RAM
        self._dc(1)
        self._cs(0)
        self._stamper.stamp()

        # Start CLUT DMA and wait for it to produce output
        self._dma_null.start()
        self._dma_in.start()
        self._clut.wait_for_output()

        # Start SPI output
        self._dma_out.start()
        self._stamper.stamp()
        self._dma_null.wait_until_done()
        self._stamper.stamp()

        self._cs(1)
        self._dc(0)
        self._stamper.end()

    async def do_refresh(self, split=4):
        def show_and_signal_done():
            self.show()
            self._do_refresh_done = True

        async with self._lock:
            self._do_refresh_done = False
            _thread.start_new_thread(show_and_signal_done, ())
            while not self._do_refresh_done:
                await asyncio.sleep_ms(0)
