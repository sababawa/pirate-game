import pygame
import math
import random
from engine.settings import (PLAYER_MAX_HEALTH, PLAYER_MAX_SPEED, PLAYER_TURN_SPEED,
                              PLAYER_ACCELERATION, CANNON_DAMAGE, CANNON_COOLDOWN,
                              CANNON_SPEED, WORLD_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
from engine.utils import vec2_from_angle, normalize_angle
from assets.generator import generate_player_ship
from entities.cannonball import Cannonball


_player_sprite = None


def _get_sprite():
    global _player_sprite
    if _player_sprite is None:
        _player_sprite = generate_player_ship(64)
    return _player_sprite


class PlayerShip:
    def __init__(self, pos):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0.0  # 0 = north/up
        self.angular_vel = 0.0
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.gold = 0
        self.sail_level = 0.0
        self.cannon_cooldown_left = 0.0
        self.cannon_cooldown_right = 0.0
        self.wake_points = []
        self.alive = True
        self.at_dock = False
        self.near_treasure = None
        self.radius = 20
        self._current_speed = 0.0
        self._sail_input = 0  # -1, 0, 1
        self._turn_input = 0  # -1, 0, 1
        self._wake_timer = 0.0
        self._frame = 0

    def handle_input(self, keys, events):
        """Process input. Returns list of new Cannonball objects."""
        # Sail
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self._sail_input = 1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self._sail_input = -1
        else:
            self._sail_input = 0

        # Turn
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self._turn_input = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self._turn_input = 1
        else:
            self._turn_input = 0

        # Fire on SPACE keydown
        new_balls = []
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                new_balls = self.fire_cannons('both')
        return new_balls

    def update(self, dt, wind_angle, wind_speed, islands, rocks):
        # Sail level
        sail_rate = 0.5
        if self._sail_input == 1:
            self.sail_level = min(1.0, self.sail_level + sail_rate * dt)
        elif self._sail_input == -1:
            self.sail_level = max(0.0, self.sail_level - sail_rate * dt)

        # Turn
        if self._turn_input != 0:
            self.angular_vel += PLAYER_TURN_SPEED * self._turn_input * dt * 60 * dt
        self.angular_vel *= 0.85
        self.angle = normalize_angle(self.angle + self.angular_vel)

        # Wind alignment (0=sailing against wind, 1=sailing with wind)
        angle_diff_rad = math.radians(self.angle - wind_angle)
        wind_alignment = (1 + math.cos(angle_diff_rad)) / 2

        target_speed = self.sail_level * PLAYER_MAX_SPEED * wind_alignment * wind_speed
        speed_diff = target_speed - self._current_speed
        self._current_speed += speed_diff * min(1.0, PLAYER_ACCELERATION * dt / max(abs(speed_diff), 1.0))

        # Apply velocity
        fwd = vec2_from_angle(self.angle)
        self.pos.x += fwd[0] * self._current_speed * dt
        self.pos.y += fwd[1] * self._current_speed * dt

        # Island collision
        for island in islands:
            d = math.sqrt((self.pos.x - island.pos.x) ** 2 + (self.pos.y - island.pos.y) ** 2)
            min_dist = island.radius * 0.82 + self.radius
            if d < min_dist and d > 0:
                nx = (self.pos.x - island.pos.x) / d
                ny = (self.pos.y - island.pos.y) / d
                self.pos.x = island.pos.x + nx * min_dist
                self.pos.y = island.pos.y + ny * min_dist
                self._current_speed *= 0.5

        # Rock collision
        for rock in rocks:
            rx, ry = rock['pos']
            d = math.sqrt((self.pos.x - rx) ** 2 + (self.pos.y - ry) ** 2)
            min_dist = rock['radius'] + self.radius
            if d < min_dist and d > 0:
                nx = (self.pos.x - rx) / d
                ny = (self.pos.y - ry) / d
                self.pos.x = rx + nx * min_dist
                self.pos.y = ry + ny * min_dist
                self._current_speed *= 0.4

        # World bounds
        self.pos.x = max(self.radius, min(WORLD_SIZE - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WORLD_SIZE - self.radius, self.pos.y))

        # Cannon cooldowns
        self.cannon_cooldown_left = max(0.0, self.cannon_cooldown_left - dt)
        self.cannon_cooldown_right = max(0.0, self.cannon_cooldown_right - dt)

        # Wake trail
        self._wake_timer += dt
        if self._wake_timer > 0.1 and self._current_speed > 10:
            self._wake_timer = 0.0
            self.wake_points.append(pygame.math.Vector2(self.pos))
            if len(self.wake_points) > 20:
                self.wake_points.pop(0)
        elif self._current_speed <= 10 and self._wake_timer > 0.3:
            self._wake_timer = 0.0

    def fire_cannons(self, direction='both'):
        balls = []
        if direction in ('left', 'both') and self.cannon_cooldown_left <= 0:
            self.cannon_cooldown_left = CANNON_COOLDOWN
            for spread in (-5, 0, 5):
                fire_angle = self.angle - 90 + spread
                balls.append(Cannonball(
                    (self.pos.x, self.pos.y),
                    fire_angle,
                    CANNON_SPEED,
                    CANNON_DAMAGE,
                    owner='player'
                ))
        if direction in ('right', 'both') and self.cannon_cooldown_right <= 0:
            self.cannon_cooldown_right = CANNON_COOLDOWN
            for spread in (-5, 0, 5):
                fire_angle = self.angle + 90 + spread
                balls.append(Cannonball(
                    (self.pos.x, self.pos.y),
                    fire_angle,
                    CANNON_SPEED,
                    CANNON_DAMAGE,
                    owner='player'
                ))
        return balls

    def repair(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen((self.pos.x, self.pos.y))

        # Wake trail
        if len(self.wake_points) >= 2:
            for i in range(1, len(self.wake_points)):
                p1x, p1y = camera.world_to_screen((self.wake_points[i - 1].x, self.wake_points[i - 1].y))
                p2x, p2y = camera.world_to_screen((self.wake_points[i].x, self.wake_points[i].y))
                alpha = int(i / len(self.wake_points) * 100)
                wake_w = max(1, i // 4)
                try:
                    pygame.draw.line(surface, (150, 200, 240), (int(p1x), int(p1y)), (int(p2x), int(p2y)), wake_w)
                except Exception:
                    pass

        # Ship sprite
        sprite = _get_sprite()
        rotated = pygame.transform.rotate(sprite, -self.angle)
        hw = rotated.get_width() // 2
        hh = rotated.get_height() // 2
        surface.blit(rotated, (int(sx) - hw, int(sy) - hh))

        # Health bar (only when damaged)
        if self.health < self.max_health:
            bar_w = 50
            bar_h = 6
            bx = int(sx) - bar_w // 2
            by = int(sy) - self.radius - 16
            ratio = self.health / self.max_health
            pygame.draw.rect(surface, (60, 10, 10), (bx, by, bar_w, bar_h))
            bar_color = (50, 200, 50) if ratio > 0.6 else (220, 180, 0) if ratio > 0.3 else (220, 50, 50)
            pygame.draw.rect(surface, bar_color, (bx, by, int(bar_w * ratio), bar_h))
            pygame.draw.rect(surface, (200, 200, 200), (bx, by, bar_w, bar_h), 1)
