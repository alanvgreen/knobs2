# Splash screen
# Shows on startup and then is covered by the main screen
import asyncio

from gui.core.tgui import Screen, Widget, ssd, display
from gui.core.writer import CWriter

import myfonts.poetsen_70 as title_font
import myfonts.poetsen_30 as sub_font
import myfonts.poppins_semi_15 as content_font

from colors import GREEN, YELLOW, WHITE, BLACK, RED

class SplashWidget(Widget):
    def __init__(self, wri: CWriter, cb):
        super().__init__(wri, 4, 4, 312, 232, YELLOW, BLACK, RED, active=True)
        self._cb = cb

    def show(self):
        super().show(black=False)
        wri = self.writer
        w = wri.stringlen("knobs")
        col = (240 - w) // 2
        display.print_left(wri, col, 70, "knobs")
        wri2 = CWriter(ssd, sub_font, GREEN, BLACK, verbose=False)
        display.print_left(wri2, col, 140, "but no sliders")
        wri3 = CWriter(ssd, content_font, WHITE, BLACK, verbose=False)

        w2 = wri3.stringlen("A Mitchell Green design")
        col = col + w - w2
        display.print_left(wri3, col, 280, "A Mitchell Green design")

    def _touched(self, rr, rc):
        pass

    def _untouched(self):
        if self._cb:
            self._cb()


class SplashScreen(Screen):
    def __init__(self, timeout_ms: int, exit_cb):
        super().__init__()
        wri = CWriter(ssd, title_font, YELLOW, BLACK, verbose=False)
        SplashWidget(wri, exit_cb)

        async def cb_on_timeout():
            await asyncio.sleep_ms(timeout_ms)
            if Screen.current_screen == self:
                exit_cb()

        asyncio.create_task(cb_on_timeout())
