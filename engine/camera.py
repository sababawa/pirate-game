import pygame
import math
import random
from engine.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_SIZE, CAMERA_LAG


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.offset = pygame.math.Vector2(0, 0)
        self.target_offset = pygame.math.Vector2(0, 0)
        self.shake_intensity = 0.0
        self.shake_timer = 0.0
        self.zoom = 1.0

    def update(self, target_pos, dt):
        # Target: centre screen on target
        self.target_offset.x = target_pos[0] - self.width // 2
        self.target_offset.y = target_pos[1] - self.height // 2

        # Clamp target to world bounds
        self.target_offset.x = max(0, min(WORLD_SIZE - self.width, self.target_offset.x))
        self.target_offset.y = max(0, min(WORLD_SIZE - self.height, self.target_offset.y))

        # Smooth follow
        t = min(1.0, dt / max(CAMERA_LAG, 0.001))
        self.offset.x += (self.target_offset.x - self.offset.x) * t
        self.offset.y += (self.target_offset.y - self.offset.y) * t

        # Screen shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            sx = random.uniform(-self.shake_intensity, self.shake_intensity)
            sy = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.offset.x += sx
            self.offset.y += sy
        else:
            self.shake_intensity = 0.0

    def add_shake(self, intensity):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_timer = 0.3

    def world_to_screen(self, world_pos):
        return (world_pos[0] - self.offset.x, world_pos[1] - self.offset.y)

    def screen_to_world(self, screen_pos):
        return (screen_pos[0] + self.offset.x, screen_pos[1] + self.offset.y)
