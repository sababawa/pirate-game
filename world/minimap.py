import pygame
import math
from engine.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_SIZE
from engine.utils import vec2_from_angle


class Minimap:
    def __init__(self, map_size=200):
        self.map_size = map_size
        self.is_fullmap = False
        self.padding = 10

    def toggle_fullmap(self):
        self.is_fullmap = not self.is_fullmap

    def draw(self, surface, player, islands, enemies, treasures, world_size=WORLD_SIZE):
        if self.is_fullmap:
            self._draw_fullmap(surface, player, islands, enemies, treasures, world_size)
        else:
            self._draw_minimap(surface, player, islands, enemies, treasures, world_size)

    def _draw_minimap(self, surface, player, islands, enemies, treasures, world_size):
        ms = self.map_size
        pad = self.padding
        mx = SCREEN_WIDTH - ms - pad
        my = SCREEN_HEIGHT - ms - pad

        # Background
        bg = pygame.Surface((ms, ms), pygame.SRCALPHA)
        bg.fill((10, 20, 50, 200))
        surface.blit(bg, (mx, my))
        pygame.draw.rect(surface, (100, 130, 200), (mx, my, ms, ms), 2)

        scale = ms / world_size

        def to_map(wx, wy):
            return (mx + int(wx * scale), my + int(wy * scale))

        # Islands
        for isl in islands:
            px, py = to_map(isl.pos.x, isl.pos.y)
            r = max(3, int(isl.radius * scale * 1.5))
            if mx <= px <= mx + ms and my <= py <= my + ms:
                pygame.draw.circle(surface, (60, 140, 60), (px, py), r)

        # Treasures
        for t in treasures:
            if t.alive:
                px, py = to_map(t.pos.x, t.pos.y)
                if mx <= px <= mx + ms and my <= py <= my + ms:
                    pygame.draw.circle(surface, (255, 215, 0), (px, py), 2)

        # Enemies
        for e in enemies:
            if e.alive:
                px, py = to_map(e.pos.x, e.pos.y)
                if mx <= px <= mx + ms and my <= py <= my + ms:
                    pygame.draw.circle(surface, (220, 50, 50), (px, py), 2)

        # Player
        ppx, ppy = to_map(player.pos.x, player.pos.y)
        ppx = max(mx, min(mx + ms, ppx))
        ppy = max(my, min(my + ms, ppy))
        pygame.draw.circle(surface, (255, 255, 255), (ppx, ppy), 3)
        dx, dy = vec2_from_angle(player.angle)
        pygame.draw.line(surface, (255, 255, 255),
                         (ppx, ppy), (ppx + int(dx * 6), ppy + int(dy * 6)), 1)

        # Label
        try:
            font = pygame.font.Font(None, 16)
            lbl = font.render('M:MAP', True, (180, 200, 255))
            surface.blit(lbl, (mx + 4, my + 4))
        except Exception:
            pass

    def _draw_fullmap(self, surface, player, islands, enemies, treasures, world_size):
        fms = min(SCREEN_WIDTH, SCREEN_HEIGHT) - 80
        fx = (SCREEN_WIDTH - fms) // 2
        fy = (SCREEN_HEIGHT - fms) // 2

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        bg = pygame.Surface((fms, fms), pygame.SRCALPHA)
        bg.fill((10, 20, 50, 240))
        surface.blit(bg, (fx, fy))
        pygame.draw.rect(surface, (100, 130, 200), (fx, fy, fms, fms), 3)

        scale = fms / world_size

        def to_map(wx, wy):
            return (fx + int(wx * scale), fy + int(wy * scale))

        for isl in islands:
            px, py = to_map(isl.pos.x, isl.pos.y)
            r = max(4, int(isl.radius * scale * 1.5))
            pygame.draw.circle(surface, (60, 140, 60), (px, py), r)
            color = {'town': (255, 220, 0), 'fort': (200, 50, 50), 'wilderness': (80, 180, 80)}
            pygame.draw.circle(surface, color.get(isl.island_type, (80, 180, 80)), (px, py), max(2, r // 2))

        for t in treasures:
            if t.alive:
                px, py = to_map(t.pos.x, t.pos.y)
                pygame.draw.circle(surface, (255, 215, 0), (px, py), 3)

        for e in enemies:
            if e.alive:
                px, py = to_map(e.pos.x, e.pos.y)
                pygame.draw.circle(surface, (220, 50, 50), (px, py), 3)

        ppx, ppy = to_map(player.pos.x, player.pos.y)
        pygame.draw.circle(surface, (255, 255, 255), (ppx, ppy), 5)
        dx, dy = vec2_from_angle(player.angle)
        pygame.draw.line(surface, (255, 255, 255),
                         (ppx, ppy), (ppx + int(dx * 10), ppy + int(dy * 10)), 2)

        try:
            font = pygame.font.Font(None, 22)
            lbl = font.render('WORLD MAP  [M] to close', True, (180, 200, 255))
            surface.blit(lbl, (fx + 8, fy + 8))
        except Exception:
            pass
