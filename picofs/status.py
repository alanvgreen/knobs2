import asyncio
from time import ticks_ms, ticks_add, ticks_diff

from gui.core.colors import GREEN, YELLOW, WHITE, BLACK, RED
from gui.core.tgui import Screen, ssd
from gui.core.writer import CWriter
from gui.widgets.buttons import Button
from gui.widgets.knob import Knob, TWOPI

import myfonts.poppins_semi_15 as font


HIGHLIGHT_RESET_MS = 500
NORMAL_COLOR = YELLOW
HIGHLIGHT_COLOR = WHITE


class StatusScreen(Screen):
    """The main info screen shows the pot state."""

    def __init__(self, pot_holder, settings_cb):
        super().__init__()
        self._knobs = []
        self._reset_ticks = []
        wri = CWriter(ssd, font, RED, YELLOW, verbose=False)
        self._build_knobs(wri)  # Populate self._knobs and _reset_ticks

        Button(wri, 255, 5, height=50, width=80, text="Settings", callback=settings_cb)

        self.reg_task(self._highlight_reset())
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
                color=NORMAL_COLOR,
                bgcolor=BLACK,
                bdcolor=False,
            )
            self._knobs.append(k)
            self._reset_ticks.append(None)

        for y in range(4):
            for x in range(4):
                knob(row=5 + 60 * y, col=5 + 60 * x, height=50)
        knob(row=250, col=95, height=60)
        knob(row=250, col=170, height=60)

    def _on_pot_changed(self, idx, val):
        """Sets a value (0-127) into a knob"""
        self._knobs[idx].value(val / 127)
        self._knobs[idx].color = HIGHLIGHT_COLOR
        self._reset_ticks[idx] = ticks_add(ticks_ms(), HIGHLIGHT_RESET_MS)

    async def _highlight_reset(self):
        # Reset background color after a time.
        wait_ms = HIGHLIGHT_RESET_MS
        while True:
            now = ticks_ms()
            wait_ms = HIGHLIGHT_RESET_MS

            # Check whether each knob will (or does) need a reset
            for idx in range(len(self._reset_ticks)):
                if self._reset_ticks[idx] is not None:
                    d = ticks_diff(self._reset_ticks[idx], now)
                    if d > 0:
                        # There will be a reset in future
                        wait_ms = min(wait_ms, d)
                    else:
                        # Reset scheduled for past - do reset now
                        self._knobs[idx].color = NORMAL_COLOR
                        self._knobs[idx].draw = True
                        self._reset_ticks[idx] = None

            await asyncio.sleep_ms(wait_ms)
