import hardware_setup  # Create a display instance
from gui.core.tgui import Screen, Window, ssd
from gui.core.writer import CWriter
import myfonts.poetsen_60 as title_font
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


class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, title_font, GREEN, BLACK, verbose=False)
        Label(wri, 0, 0, "Knobs")


def start():
    Screen.change(BaseScreen)
