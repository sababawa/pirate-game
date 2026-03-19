import pygame
import math
import random
from engine.settings import (SLOOP_SPEED, SLOOP_HEALTH, GALLEON_SPEED, GALLEON_HEALTH,
                              AGGRO_RANGE, CANNON_RANGE, CANNON_SPEED, CANNON_DAMAGE,
                              ENEMY_FIRE_COOLDOWN_MIN, ENEMY_FIRE_COOLDOWN_MAX,
                              SCREEN_WIDTH, SCREEN_HEIGHT)
from engine.utils import distance, vec2_from_angle, normalize_angle
from assets.generator import generate_enemy_ship


_enemy_sprites = {}


def _get_sprite(ship_type):
    if ship_type not in _enemy_sprites:
        _enemy_sprites[ship_type] = generate_enemy_ship(64, ship_type)
    return _enemy_sprites[ship_type]


class EnemyShip:
    PATROL = 0
    CHASE = 1
    ATTACK = 2
    RETREAT = 3
    DEAD = 4

    def __init__(self, pos, ship_type='sloop'):
        self.pos = pygame.math.Vector2(pos)
        self.ship_type = ship_type
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = random.uniform(0, 360)
        self.alive = True
        self.loot_dropped = False
        self.state = EnemyShip.PATROL

        if ship_type == 'galleon':
            self.max_health = GALLEON_HEALTH
            self.speed = GALLEON_SPEED
            self.radius = 35
        else:
            self.max_health = SLOOP_HEALTH
            self.speed = SLOOP_SPEED
            self.radius = 25

        self.health = self.max_health
        self.fire_timer = random.uniform(ENEMY_FIRE_COOLDOWN_MIN, ENEMY_FIRE_COOLDOWN_MAX)
        self.damage_smoke_timer = 0.0

        # Patrol waypoints (square pattern around spawn)
        spread = 300
        sx, sy = float(pos[0]), float(pos[1])
        self.waypoints = [
            pygame.math.Vector2(sx + spread, sy),
            pygame.math.Vector2(sx + spread, sy + spread),
            pygame.math.Vector2(sx, sy + spread),
            pygame.math.Vector2(sx, sy),
        ]
        self.current_waypoint = 0

        # Sink animation
        self.sink_timer = 0.0
        self.sink_alpha = 255

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.state = EnemyShip.DEAD
            self.alive = False

    def update(self, dt, player, islands):
        if self.state == EnemyShip.DEAD:
            return []

        self.fire_timer -= dt
        self.damage_smoke_timer -= dt

        dist_to_player = distance((self.pos.x, self.pos.y), (player.pos.x, player.pos.y))

        # State transitions
        if self.state == EnemyShip.PATROL:
            if dist_to_player < AGGRO_RANGE:
                self.state = EnemyShip.CHASE

        elif self.state == EnemyShip.CHASE:
            if dist_to_player > AGGRO_RANGE * 1.5:
                self.state = EnemyShip.PATROL
            elif dist_to_player < CANNON_RANGE * 0.9:
                self.state = EnemyShip.ATTACK

        elif self.state == EnemyShip.ATTACK:
            if dist_to_player > CANNON_RANGE * 1.1:
                self.state = EnemyShip.CHASE
            if self.health < self.max_health * 0.25:
                self.state = EnemyShip.RETREAT

        elif self.state == EnemyShip.RETREAT:
            if dist_to_player > AGGRO_RANGE * 2.0:
                self.state = EnemyShip.PATROL

        # Movement
        if self.state == EnemyShip.PATROL:
            target = self.waypoints[self.current_waypoint]
            self._steer_toward(target, dt, self.speed * 0.7)
            if distance((self.pos.x, self.pos.y), (target.x, target.y)) < 30:
                self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)

        elif self.state == EnemyShip.CHASE:
            self._steer_toward(player.pos, dt, self.speed)

        elif self.state == EnemyShip.ATTACK:
            # Strafe to get broadside
            dx = player.pos.x - self.pos.x
            dy = player.pos.y - self.pos.y
            perp = pygame.math.Vector2(-dy, dx)
            if perp.length() > 0:
                perp = perp.normalize()
            strafe_target = pygame.math.Vector2(
                self.pos.x + perp.x * 150,
                self.pos.y + perp.y * 150,
            )
            self._steer_toward(strafe_target, dt, self.speed * 0.8)

        elif self.state == EnemyShip.RETREAT:
            dx = self.pos.x - player.pos.x
            dy = self.pos.y - player.pos.y
            flee = pygame.math.Vector2(dx, dy)
            if flee.length() > 0:
                flee = flee.normalize()
            flee_target = pygame.math.Vector2(
                self.pos.x + flee.x * 200,
                self.pos.y + flee.y * 200,
            )
            self._steer_toward(flee_target, dt, self.speed * 1.1)

        # Move
        fwd = vec2_from_angle(self.angle)
        self.pos.x += fwd[0] * self.speed * dt
        self.pos.y += fwd[1] * self.speed * dt

        # World bounds
        from engine.settings import WORLD_SIZE
        self.pos.x = max(self.radius, min(WORLD_SIZE - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WORLD_SIZE - self.radius, self.pos.y))

        # Firing
        new_balls = []
        if self.state in (EnemyShip.ATTACK,) and self.fire_timer <= 0:
            if dist_to_player < CANNON_RANGE:
                self.fire_timer = random.uniform(ENEMY_FIRE_COOLDOWN_MIN, ENEMY_FIRE_COOLDOWN_MAX)
                new_balls = self._fire_at(player)

        return new_balls

    def _steer_toward(self, target, dt, speed):
        dx = target[0] - self.pos.x
        dy = target[1] - self.pos.y
        if abs(dx) < 1 and abs(dy) < 1:
            return
        target_angle = math.degrees(math.atan2(dx, -dy)) % 360
        diff = (target_angle - self.angle + 180) % 360 - 180
        turn_rate = 80.0
        max_turn = turn_rate * dt
        self.angle += max(-max_turn, min(max_turn, diff))
        self.angle = normalize_angle(self.angle)

    def _fire_at(self, player):
        from entities.cannonball import Cannonball
        balls = []
        # Both broadside angles
        for side_offset in (-90, 90):
            fire_angle = self.angle + side_offset + random.uniform(-8, 8)
            balls.append(Cannonball(
                (self.pos.x, self.pos.y),
                fire_angle,
                CANNON_SPEED,
                CANNON_DAMAGE,
                owner='enemy'
            ))
        return balls

    def drop_loot(self):
        from entities.treasure import Treasure
        loot = []
        tier = Treasure.BRONZE
        if self.ship_type == 'galleon':
            tier = random.choice([Treasure.SILVER, Treasure.GOLD])
        else:
            tier = random.choice([Treasure.BRONZE, Treasure.BRONZE, Treasure.SILVER])
        loot.append(Treasure(pygame.math.Vector2(self.pos.x + random.uniform(-30, 30),
                                                  self.pos.y + random.uniform(-30, 30)), tier))
        return loot

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen((self.pos.x, self.pos.y))

        # Cull
        size = self.radius * 3
        if sx < -size or sx > SCREEN_WIDTH + size or sy < -size or sy > SCREEN_HEIGHT + size:
            return

        sprite = _get_sprite(self.ship_type)
        rotated = pygame.transform.rotate(sprite, -self.angle)
        hw = rotated.get_width() // 2
        hh = rotated.get_height() // 2

        if not self.alive:
            rotated.set_alpha(100)
        elif self.health < self.max_health * 0.5:
            rotated.set_alpha(220)

        surface.blit(rotated, (int(sx) - hw, int(sy) - hh))

        # Health bar if damaged
        if self.alive and self.health < self.max_health:
            bar_w = 40
            bar_h = 5
            bx = int(sx) - bar_w // 2
            by = int(sy) - self.radius - 12
            ratio = self.health / self.max_health
            pygame.draw.rect(surface, (60, 10, 10), (bx, by, bar_w, bar_h))
            bar_color = (50, 200, 50) if ratio > 0.6 else (220, 180, 0) if ratio > 0.3 else (220, 50, 50)
            pygame.draw.rect(surface, bar_color, (bx, by, int(bar_w * ratio), bar_h))
            pygame.draw.rect(surface, (200, 200, 200), (bx, by, bar_w, bar_h), 1)

        # State indicator (debug-style tiny dot)
        state_colors = {
            EnemyShip.PATROL: (100, 100, 200),
            EnemyShip.CHASE: (220, 180, 0),
            EnemyShip.ATTACK: (220, 50, 50),
            EnemyShip.RETREAT: (100, 200, 100),
        }
        dot_color = state_colors.get(self.state, (128, 128, 128))
        pygame.draw.circle(surface, dot_color, (int(sx), int(sy) - self.radius - 5), 3)
