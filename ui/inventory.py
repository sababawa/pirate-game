import pygame
from engine.settings import GOLD_COLOR, WHITE
from assets.generator import get_font


class Inventory:
    def __init__(self):
        self._font = None

    def draw(self, surface, player):
        if self._font is None:
            self._font = get_font(20)
        # Minimalistic - gold is shown in HUD; this can be extended
        pass
