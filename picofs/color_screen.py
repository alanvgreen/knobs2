# Color screen
# Shows on startup and then is covered by the main screen
import asyncio

from gui.core.tgui import Screen, Widget, ssd, display
from gui.core.writer import CWriter

from gui.widgets.buttons import CloseButton

import myfonts.poppins_semi_18 as label_font
import myfonts.poppins_semi_15 as content_font

from colors import GREEN, YELLOW, WHITE, BLACK, RED

class ColorWidget(Widget):
    def __init__(self, wri: CWriter):
        super().__init__(
            writer=wri,
            row=0,
            col=0,
            height=320,
            width=240,
            fgcolor=None,
            bgcolor=None,
            bdcolor=None,
        )
        self._wri = wri

    def show(self):
        super().show(black=False)
        for y in range(4):
            for x in range(4):
                xpos,ypos,col = x*60,y*80,x+y*4
                ssd.rect(xpos,ypos, 59, 79, col, True)
                display.print_centred(self._wri, xpos+30, ypos+70, f"{col:04b}")


class ColorScreen(Screen):
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, content_font, GREEN, BLACK, verbose=False)
        ColorWidget(wri)

        close_wri = CWriter(ssd, label_font, GREEN, BLACK, verbose=False)
        CloseButton(close_wri, bgcolor=BLACK)
