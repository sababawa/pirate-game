import pygame
from engine.settings import GOLD_COLOR, WHITE
from assets.generator import get_font


class Inventory:
    def __init__(self):
        self._font = None

    def draw(self, surface, player):
        if self._font is None:
            self._font = get_font(20)
        gold_text = self._font.render(f"Gold: {player.gold}", True, GOLD_COLOR)
        bg = pygame.Surface((gold_text.get_width() + 16, gold_text.get_height() + 8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        x = surface.get_width() // 2 - bg.get_width() // 2
        y = surface.get_height() - bg.get_height() - 8
        surface.blit(bg, (x, y))
        surface.blit(gold_text, (x + 8, y + 4))
