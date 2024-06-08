# Settings page
from config import CONFIG

from gui.core.colors import GREEN, YELLOW, WHITE, BLACK, RED
from gui.core.writer import CWriter
from gui.core.tgui import Screen, ssd
from gui.widgets.buttons import CloseButton

import myfonts.poppins_semi_15 as font

class SettingsScreen(Screen):
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, font, RED, BLACK, verbose=False)
        CloseButton(wri, bgcolor=BLACK)
        CONFIG.read()


    def onhide(self):
        CONFIG.write()
