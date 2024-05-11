import asyncio

from gui.core.colors import GREEN, YELLOW, WHITE, BLACK, RED
from gui.core.tgui import Screen, ssd
from gui.core.writer import CWriter
from gui.widgets.knob import Knob, TWOPI

import myfonts.poppins_semi_15 as font

from title import TitleScreen


class InfoScreen(Screen):
    """The main info screen shows the pot state."""

    def __init__(self, pot_holder):
        super().__init__()
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)
        self._knobs = []
        self.build_knobs(wri)  # Populate self._knobs
        pot_holder.add_callback(self._on_pot_changed)

    def build_knobs(self, wri):
        def knob(row, col, height):
            k = Knob(
                row=row,
                col=col,
                height=height,
                writer=wri,
                arc=TWOPI * 0.75,
                ticks=9,
                value=0.0,
            )
            self._knobs.append(k)

        for y in range(4):
            for x in range(4):
                knob(row=10 + 40 * y, col=45 + 40 * x, height=30)
        knob(row=170, col=45, height=70)
        knob(row=170, col=125, height=70)

    def _on_pot_changed(self, idx, val):
        """Sets a value (0-127) into a knob"""
        self._knobs[idx].value(val/127)
