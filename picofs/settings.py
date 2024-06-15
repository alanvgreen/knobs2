# Settings page
from config import CONFIG

from gui.core.colors import GREEN, YELLOW, WHITE, BLACK, RED
from gui.core.writer import CWriter
from gui.core.tgui import Screen, ssd
from gui.widgets.buttons import Button, CloseButton
from gui.widgets.label import Label

import myfonts.poppins_semi_15 as font
import myfonts.poppins_semi_18 as label_font
import myfonts.poppins_bold_30 as title_font

LIST_SIXTEEN = [str(i + 1) for i in range(16)]
# LIST_SIXTEEN = ["1", "2", "3"]


class ChannelButton(Button):
    # Kind of a radio button
    def __init__(self, writer, row, col, text):
        super().__init__(
            writer,
            row,
            col,
            height=20,
            width=24,
            fgcolor=WHITE,
            bgcolor=BLACK,
            text=text,
        )



class SettingsScreen(Screen):
    def __init__(self):
        super().__init__()
        title_wri = CWriter(ssd, title_font, WHITE, BLACK, verbose=False)
        Label(title_wri, 10, 0, text=210, justify=1).value("Channels")

        label_wri = CWriter(ssd, label_font, GREEN, BLACK, verbose=False)
        CloseButton(label_wri, bgcolor=BLACK)
        CONFIG.read()

        self._banks = []
        value_wri = CWriter(ssd, font, WHITE, BLACK, verbose=False)
        for i in range(5):
            self._banks.append(self._add_channel(label_wri, value_wri, i))

    def _add_channel(self, label_wri, value_wri, idx):
        c = chr(ord("A") + idx)
        row = 60 + 52 * idx
        Label(label_wri, row, 0, 24, justify=1).value(c)

        buttons = []
        for i in range(2):
            for j in range(8):
                b = ChannelButton(
                    value_wri,
                    row + i * 20,
                    24 + 24 * j,
                    str(1 + j + i * 8),
                )
                buttons.append(b)
        return buttons

    def onhide(self):
        CONFIG.write()
