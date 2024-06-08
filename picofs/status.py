import asyncio
from time import ticks_ms, ticks_add, ticks_diff

from gui.core.colors import GREEN, YELLOW, WHITE, BLACK, RED
from gui.core.tgui import Screen, ssd
from gui.core.writer import CWriter
from gui.widgets.knob import Knob, TWOPI

import myfonts.poppins_semi_15 as font


BG_RESET_MS = 500


class StatusScreen(Screen):
    """The main info screen shows the pot state."""

    def __init__(self, pot_holder):
        super().__init__()
        self._knobs = []
        self._reset_ticks = []
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False) # sets initial colors
        print("building started")
        self._build_knobs(wri)  # Populate self._knobs and _reset_ticks
        print("building done")
        self.reg_task(self._bg_reset())
        pot_holder.add_callback(self._on_pot_changed)

    def _build_knobs(self, wri):
        def knob(row, col, height):
            k = Knob(
                row=row,
                col=col,
                height=height,
                writer=wri,
                arc=TWOPI * 0.75,
                ticks=9,
                value=0.0,
                active=False,
                fgcolor=RED,
                color=YELLOW,
                bgcolor=BLACK,
                bdcolor=False,
            )
            self._knobs.append(k)
            self._reset_ticks.append(None)

        for y in range(4):
            for x in range(4):
                knob(row=5+ 60 * y, col=5 + 60 * x, height=50)
        knob(row=245, col=45, height=70)
        knob(row=245, col=125, height=70)

    def _on_pot_changed(self, idx, val):
        """Sets a value (0-127) into a knob"""
        self._knobs[idx].value(val/127)
        self._knobs[idx].bgcolor = WHITE
        self._reset_ticks[idx] = ticks_add(ticks_ms(), BG_RESET_MS)

    async def _bg_reset(self):
        await asyncio.sleep_ms(2)
        wait_ms = BG_RESET_MS
        while True:
            # Wait an appropriate time
            print(f"sleep {wait_ms}")
            await asyncio.sleep_ms(wait_ms)
            wait_ms = BG_RESET_MS
            now = ticks_ms()

            # Check every reset
            for idx in range(len(self._reset_ticks)):
                if self._reset_ticks[idx] is not None:
                    d = ticks_diff(self._reset_ticks[idx], now)
                    if d > 0:
                        # There will be a reset in future
                        wait_ms = min(wait_ms, d)
                    else:
                        # Reset scheduled for past - do reset now
                        self._knobs[idx].bgcolor = BLACK
                        self._knobs[idx].draw = True
                        self._reset_ticks[idx] = None

