# Title screen
# Shows on startup and then is covered by the main screen

from gui.core.tgui import Screen, Widget, ssd, display
from gui.core.writer import CWriter
from gui.core.colors import GREEN, YELLOW, WHITE, BLACK, RED

import myfonts.poetsen_70 as title_font
import myfonts.poetsen_30 as sub_font
import myfonts.poppins_semi_15 as content_font


class TitleWidget(Widget):
    def __init__(self, wri: CWriter):
        super().__init__(wri, 4, 4, 312, 232, YELLOW, BLACK, RED)

    def show(self):
        super().show(black=False)
        wri = self.writer
        w = wri.stringlen("knobs")
        print(w)
        col = (240 - w) // 2
        print(col)
        display.print_left(wri, col, 70, "knobs")
        wri2 = CWriter(ssd, sub_font, GREEN, BLACK, verbose=False)
        display.print_left(wri2, col, 140, "but no sliders")
        wri3 = CWriter(ssd, content_font, WHITE, BLACK, verbose=False)

        w2 = wri3.stringlen("A Mitchell Green design")
        col = col + w - w2
        display.print_left(wri3, col, 280, "A Mitchell Green design")


class TitleScreen(Screen):
    def __init__(self, timeout: int, next_screen: Screen):
        super().__init__()
        wri = CWriter(ssd, title_font, YELLOW, BLACK, verbose=False)
        TitleWidget(wri)