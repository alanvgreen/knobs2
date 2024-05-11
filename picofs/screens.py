import hardware_setup  # Create a display instance
from gui.core.tgui import Screen, Window, ssd
from gui.core.writer import CWriter
from gui.widgets import (
    Button,
    RadioButtons,
    CloseButton,
    Listbox,
    Dropdown,
    DialogBox,
    Label,
)

from gui.core.colors import GREEN, BLACK

from title import TitleScreen


class MainScreen(Screen):
    pass


def start():
    Screen.change(TitleScreen, kwargs=dict(timeout=60, next_screen=MainScreen))
