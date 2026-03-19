import pygame
import math
from engine.settings import CANNON_RANGE, CANNON_SPEED
from engine.utils import distance
from assets.generator import generate_cannon_ball


_cb_sprite = None


def _get_sprite():
    global _cb_sprite
    if _cb_sprite is None:
        _cb_sprite = generate_cannon_ball(6)
    return _cb_sprite


class Cannonball:
    def __init__(self, pos, angle, speed, damage, owner='player'):
        self.pos = [float(pos[0]), float(pos[1])]
        dx = math.sin(math.radians(angle))
        dy = -math.cos(math.radians(angle))
        self.vel = [dx * speed, dy * speed]
        self.damage = damage
        self.owner = owner
        self.alive = True
        self.hit_pos = None
        self.hit_ship = False
        self.lifetime = CANNON_RANGE / max(speed, 1.0)
        self._timer = 0.0

    def update(self, dt, islands, enemy_ships, player):
        if not self.alive:
            return

        self._timer += dt
        if self._timer >= self.lifetime:
            self.alive = False
            return

        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt

        # Collision with enemy ships (player cannonballs only)
        if self.owner == 'player':
            for ship in enemy_ships:
                if not ship.alive:
                    continue
                if distance(self.pos, (ship.pos.x, ship.pos.y)) < ship.radius + 6:
                    ship.take_damage(self.damage)
                    self.alive = False
                    self.hit_pos = (self.pos[0], self.pos[1])
                    self.hit_ship = True
                    return

        # Collision with player (enemy cannonballs only)
        if self.owner == 'enemy':
            if player.alive and distance(self.pos, (player.pos.x, player.pos.y)) < player.radius + 6:
                player.health -= self.damage
                self.alive = False
                self.hit_pos = (self.pos[0], self.pos[1])
                self.hit_ship = True
                return

        # Collision with islands
        for island in islands:
            if distance(self.pos, (island.pos.x, island.pos.y)) < island.radius * 0.85:
                self.alive = False
                self.hit_pos = (self.pos[0], self.pos[1])
                return

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.pos)
        sprite = _get_sprite()
        hw = sprite.get_width() // 2
        hh = sprite.get_height() // 2
        surface.blit(sprite, (int(sx) - hw, int(sy) - hh))
