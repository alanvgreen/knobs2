import asyncio
import random

from machine import Pin
import usb.device
from usb.device.midi import MIDIInterface

import hardware_setup  # Create a display instance
from gui.core.tgui import Screen

import adc, pots
from config import Config
from controller import Controller
from settings import SettingsScreen
from splash import SplashScreen
from status import StatusScreen


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
    led = Pin(8, Pin.OUT)
    led.value(1)

    pot_holder = pots.PotHolder()
    pot_reader = adc.PotReader(pot_holder)

    # Init MIDI USB
    midi = get_midi()
    controller = Controller(pot_holder, midi)

    # Start pot holder update
    #asyncio.create_task(twiddle(pot_holder))
    asyncio.create_task(pot_reader.loop())

    # Launch UI
    def go_settings_screen(_):
        Screen.change(SettingsScreen)

    def go_status_screen():
        Screen.change(
            StatusScreen,
            kwargs=dict(pot_holder=pot_holder, settings_cb=go_settings_screen),
        )

    go_settings_screen(None)
    print("Launch")
    Screen.change(SplashScreen, kwargs=dict(timeout_ms=300, exit_cb=go_status_screen))
