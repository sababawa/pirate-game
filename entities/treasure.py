import pygame
import math
from engine.settings import TREASURE_PICKUP_RADIUS, GOLD_COLOR
from assets.generator import generate_treasure_chest


_chest_sprites = {}


def _get_chest(tier_name):
    if tier_name not in _chest_sprites:
        _chest_sprites[tier_name] = generate_treasure_chest(tier_name)
    return _chest_sprites[tier_name]


class Treasure:
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    LEGENDARY = 3

    GOLD_VALUES = {BRONZE: 50, SILVER: 150, GOLD: 400, LEGENDARY: 1000}
    TIER_NAMES = {BRONZE: 'bronze', SILVER: 'silver', GOLD: 'gold', LEGENDARY: 'legendary'}

    def __init__(self, pos, treasure_type=0):
        self.pos = pygame.math.Vector2(pos)
        self.treasure_type = treasure_type
        self.gold_value = self.GOLD_VALUES.get(treasure_type, 50)
        self.alive = True
        self.bob_time = 0.0
        self.bob_offset = 0.0

    def update(self, dt):
        self.bob_time += dt
        self.bob_offset = math.sin(self.bob_time * 2.0) * 3.0

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen((self.pos.x, self.pos.y))
        sy += self.bob_offset

        tier_name = self.TIER_NAMES.get(self.treasure_type, 'bronze')
        sprite = _get_chest(tier_name)
        hw = sprite.get_width() // 2
        hh = sprite.get_height() // 2
        surface.blit(sprite, (int(sx) - hw, int(sy) - hh))

        # Glow ring for legendary
        if self.treasure_type == Treasure.LEGENDARY:
            r = int(16 + math.sin(self.bob_time * 3) * 3)
            glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (180, 0, 255, 60), (r, r), r)
            surface.blit(glow, (int(sx) - r, int(sy) - r))

    def can_pickup(self, player_pos):
        dx = self.pos.x - player_pos[0]
        dy = self.pos.y - player_pos[1]
        return math.sqrt(dx * dx + dy * dy) < TREASURE_PICKUP_RADIUS
