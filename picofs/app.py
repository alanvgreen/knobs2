import asyncio
import random

import hardware_setup  # Create a display instance
from gui.core.tgui import Screen

from title import TitleScreen
from info import InfoScreen
import pots


def start():
    pot_holder = pots.PotHolder()
    async def twiddle():
        for i in range(100):
            await asyncio.sleep_ms(200)
            idx = random.randrange(18)
            value = random.randrange(pots.Pot.DENOMINATOR)
            pot_holder.update(idx, value)

    asyncio.create_task(twiddle())

    Screen.change(TitleScreen, kwargs=dict(timeout_ms=300))
    Screen.change(InfoScreen, kwargs=dict(pot_holder=pot_holder))

