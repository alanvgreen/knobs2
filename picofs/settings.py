# Settings page
from config import CONFIG

from gui.core.writer import CWriter
from gui.core.tgui import Screen, ssd
from gui.widgets.buttons import Button, CloseButton
from gui.widgets.label import Label

import myfonts.poppins_semi_15 as font
import myfonts.poppins_semi_18 as label_font
import myfonts.poppins_bold_30 as title_font

LIST_SIXTEEN = [str(i + 1) for i in range(16)]

from color_screen import ColorScreen
from colors import GREEN, YELLOW, WHITE, BLACK, RED


class ChannelButton(Button):
    # Kind of a radio button
    def __init__(self, writer, row, col, cb, group_idx, channel_idx):
        super().__init__(
            writer,
            row,
            col,
            height=20,
            width=24,
            fgcolor=WHITE,
            bgcolor=BLACK,
            text=str(1 + channel_idx),
            callback=cb,
        )
        self.group_idx = group_idx
        self.channel_idx = channel_idx

    def check(self, checked):
        new_bgcolor = WHITE if checked else BLACK
        if new_bgcolor != self.bgcolor:
            self.bgcolor = new_bgcolor
            self.draw = True
        new_textcolor = BLACK if checked else WHITE
        if new_textcolor != self.textcolor:
            self.textcolor = new_textcolor
            self.draw = True


class SettingsScreen(Screen):
    def __init__(self):
        super().__init__()
        title_wri = CWriter(ssd, title_font, WHITE, BLACK, verbose=False)
        Label(title_wri, row=10, col=60, text="Channels")

        label_wri = CWriter(ssd, label_font, GREEN, BLACK, verbose=False)
        CloseButton(label_wri, bgcolor=BLACK, callback=self._on_close)
        Button(
            label_wri,
            row=4,
            col=4,
            height=30,
            width=30,
            callback=(lambda _: Screen.change(ColorScreen)),
            text="C",
            bgcolor=BLACK,
        )

        self._groups = []
        value_wri = CWriter(ssd, font, WHITE, BLACK, verbose=False)
        for i in range(5):
            self._groups.append(self._add_group(label_wri, value_wri, i))

        self._update_checks()

    def _add_group(self, label_wri, value_wri, group_idx):
        c = chr(ord("A") + group_idx)
        row = 60 + 52 * group_idx
        Label(label_wri, row, 0, 24, justify=1).value(c)

        buttons = []
        for i in range(2):
            for j in range(8):
                channel_idx = j + i * 8
                b = ChannelButton(
                    value_wri,
                    row + i * 20,
                    24 + 24 * j,
                    self._clicked,
                    group_idx,
                    channel_idx,
                )
                buttons.append(b)
        return buttons

    def _clicked(self, button):
        CONFIG.set_channel(button.group_idx, button.channel_idx)
        self._update_checks()

    def _update_checks(self):
        # Update button checks to match config
        for selected, buttons in zip(CONFIG.get_channels(), self._groups):
            for channel_idx, b in enumerate(buttons):
                b.check(channel_idx == selected)

    def _on_close(self, _):
        CONFIG.write()
