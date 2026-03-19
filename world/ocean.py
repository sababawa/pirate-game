import pygame
import math
import random
from engine.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, DEEP_WATER, MID_WATER,
                              SHALLOW_WATER, FOAM_COLOR, FOAM_WHITE, TURQUOISE, LIGHT_BLUE)


class OceanRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.wave_time = 0.0
        self.frame_count = 0
        self.wave_surf = pygame.Surface((width, height))
        self._draw_wave_surface()

    def _draw_wave_surface(self):
        t = self.wave_time
        surf = self.wave_surf
        surf.fill(DEEP_WATER)

        # Layer 1: wide dark blue waves
        for row in range(0, self.height, 18):
            pts = []
            for x in range(0, self.width + 8, 8):
                y = row + math.sin((x * 0.008) + t * 0.6) * 6 + math.cos((x * 0.005) + t * 0.4) * 4
                pts.append((x, int(y)))
            if len(pts) >= 2:
                pygame.draw.lines(surf, MID_WATER, False, pts, 2)

        # Layer 2: medium speed mid blue
        for row in range(9, self.height, 22):
            pts = []
            for x in range(0, self.width + 6, 6):
                y = row + math.sin((x * 0.012) + t * 1.0 + 1.5) * 4 + math.cos((x * 0.007) + t * 0.7) * 3
                pts.append((x, int(y)))
            if len(pts) >= 2:
                pygame.draw.lines(surf, (25, 85, 135), False, pts, 1)

        # Layer 3: turquoise lighter patches
        for row in range(0, self.height, 40):
            for col in range(0, self.width, 50):
                bx = col + int(math.sin(t * 0.5 + row * 0.05) * 15)
                by = row + int(math.cos(t * 0.4 + col * 0.04) * 10)
                pygame.draw.ellipse(surf, SHALLOW_WATER if (row + col) % 80 == 0 else TURQUOISE,
                                    (bx, by, 30, 12), 0)

        # Foam / whitecaps along wave crests
        random.seed(int(t * 4) & 0xFFFF)
        for _ in range(60):
            fx = random.randint(0, self.width)
            fy = random.randint(0, self.height)
            r = random.randint(1, 3)
            pygame.draw.circle(surf, FOAM_COLOR, (fx, fy), r)

    def update(self, dt):
        self.wave_time += dt
        self.frame_count += 1
        if self.frame_count % 3 == 0:
            self._draw_wave_surface()

    def draw(self, surface, camera, time_of_day):
        # Blit wave surface (offset by camera to create scrolling)
        ox = int(camera.offset.x) % self.width
        oy = int(camera.offset.y) % self.height

        # Tile the wave surface to cover screen
        for tx in range(-1, 2):
            for ty in range(-1, 2):
                surface.blit(self.wave_surf, (-ox + tx * self.width, -oy + ty * self.height))

        # Day/night colour tint overlay
        if time_of_day < 0.25 or time_of_day > 0.75:
            # Night
            if time_of_day > 0.75:
                alpha = int((time_of_day - 0.75) / 0.25 * 120)
            else:
                alpha = int((0.25 - time_of_day) / 0.25 * 120)
            night_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            night_surf.fill((0, 0, 40, min(alpha, 120)))
            surface.blit(night_surf, (0, 0))
        elif 0.25 <= time_of_day <= 0.5:
            # Dawn
            alpha = int((0.5 - time_of_day) / 0.25 * 40)
            dawn_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            dawn_surf.fill((80, 30, 10, alpha))
            surface.blit(dawn_surf, (0, 0))
