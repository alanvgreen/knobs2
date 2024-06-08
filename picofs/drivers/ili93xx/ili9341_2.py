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
import _thread


class ILI9341_2(ili9341.ILI9341):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._do_refresh_done = False

    async def do_refresh(self, split=4):
        def show_and_signal_done():
            self.show()
            self._do_refresh_done = True

        async with self._lock:
            self._do_refresh_done = False
            _thread.start_new_thread(show_and_signal_done, ())
            while not self._do_refresh_done:
                await asyncio.sleep_ms(10)
