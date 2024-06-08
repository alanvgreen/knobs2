import asyncio
import random

import usb.device
from usb.device.midi import MIDIInterface

import hardware_setup  # Create a display instance
from gui.core.tgui import Screen

from controller import Config, Controller
from splash import SplashScreen
from status import StatusScreen
import pots


async def twiddle(pot_holder):
    """Randomly twiddle the pot values

    For testing and debugging
    """
    while True:
        for idx in range(18):
            await asyncio.sleep_ms(800)
            # idx = random.randrange(18)
            value = random.randrange(65536)
            pot_holder.update(idx, value)


def get_midi():
    m = MIDIInterface()
    usb.device.get().init(
        m,
        manufacturer_str="Alan Green",
        product_str="knobs but no sliders",
        serial_str="0001 A plural-alpha first",
    )
    return m


def start():
    pot_holder = pots.PotHolder()

    # Init MIDI USB
    midi = get_midi()
    config = Config()
    controller = Controller(pot_holder, config, midi)

    # Start pot holder update
    asyncio.create_task(twiddle(pot_holder))

    # Launch UI
    def go_status_screen():
        Screen.change(
            StatusScreen,
            kwargs=dict(pot_holder=pot_holder, settings_cb=lambda _: print("settings")),
        )

    Screen.change(SplashScreen, kwargs=dict(timeout_ms=300, exit_cb=go_status_screen))
