import pygame
import math
import random


class ParticleSystem:
    SPLASH = 0
    SMOKE = 1
    EXPLOSION = 2
    FIRE = 3
    SPARKLE = 4
    RAIN = 5
    FOAM = 6
    WAKE = 7

    def __init__(self):
        self.particles = []

    def add_particles(self, ptype, pos, count, **kwargs):
        for _ in range(count):
            p = self._make_particle(ptype, pos, **kwargs)
            self.particles.append(p)

    def _make_particle(self, ptype, pos, **kwargs):
        x, y = pos
        if ptype == ParticleSystem.SPLASH:
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(60, 180)
            return {
                'pos': [float(x), float(y)],
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed - 40],
                'life': random.uniform(0.4, 0.8),
                'max_life': 0.8,
                'color': random.choice([(180, 210, 255), (200, 230, 255), (220, 240, 255)]),
                'size': random.uniform(2, 5),
                'type': ptype,
            }
        elif ptype == ParticleSystem.SMOKE:
            return {
                'pos': [float(x) + random.uniform(-5, 5), float(y) + random.uniform(-5, 5)],
                'vel': [random.uniform(-15, 15), random.uniform(-40, -20)],
                'life': random.uniform(0.8, 1.5),
                'max_life': 1.5,
                'color': (random.randint(100, 160), random.randint(100, 160), random.randint(100, 160)),
                'size': random.uniform(4, 10),
                'type': ptype,
            }
        elif ptype == ParticleSystem.EXPLOSION:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 250)
            return {
                'pos': [float(x), float(y)],
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'life': random.uniform(0.3, 0.7),
                'max_life': 0.7,
                'color': random.choice([(255, 120, 0), (255, 60, 0), (255, 200, 0), (200, 30, 0)]),
                'size': random.uniform(3, 8),
                'type': ptype,
            }
        elif ptype == ParticleSystem.FIRE:
            return {
                'pos': [float(x) + random.uniform(-8, 8), float(y)],
                'vel': [random.uniform(-20, 20), random.uniform(-80, -40)],
                'life': random.uniform(0.4, 0.9),
                'max_life': 0.9,
                'color': random.choice([(255, 160, 0), (255, 100, 0), (255, 200, 50)]),
                'size': random.uniform(3, 7),
                'type': ptype,
            }
        elif ptype == ParticleSystem.SPARKLE:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(40, 120)
            return {
                'pos': [float(x), float(y)],
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'life': random.uniform(0.5, 1.0),
                'max_life': 1.0,
                'color': random.choice([(255, 215, 0), (255, 240, 100), (255, 180, 0)]),
                'size': random.uniform(2, 5),
                'type': ptype,
            }
        elif ptype == ParticleSystem.FOAM:
            return {
                'pos': [float(x) + random.uniform(-10, 10), float(y) + random.uniform(-10, 10)],
                'vel': [random.uniform(-20, 20), random.uniform(-20, 20)],
                'life': random.uniform(0.5, 1.2),
                'max_life': 1.2,
                'color': (220, 240, 255),
                'size': random.uniform(3, 7),
                'type': ptype,
            }
        elif ptype == ParticleSystem.WAKE:
            return {
                'pos': [float(x) + random.uniform(-8, 8), float(y) + random.uniform(-8, 8)],
                'vel': [random.uniform(-15, 15), random.uniform(-15, 15)],
                'life': random.uniform(0.6, 1.4),
                'max_life': 1.4,
                'color': (150, 200, 240),
                'size': random.uniform(2, 6),
                'type': ptype,
            }
        else:
            return {
                'pos': [float(x), float(y)],
                'vel': [random.uniform(-50, 50), random.uniform(-50, 50)],
                'life': 1.0,
                'max_life': 1.0,
                'color': (255, 255, 255),
                'size': 3.0,
                'type': ptype,
            }

    def update(self, dt):
        alive = []
        for p in self.particles:
            p['life'] -= dt
            if p['life'] <= 0:
                continue
            p['pos'][0] += p['vel'][0] * dt
            p['pos'][1] += p['vel'][1] * dt
            # Gravity for some types
            if p['type'] in (ParticleSystem.SPLASH, ParticleSystem.EXPLOSION):
                p['vel'][1] += 200 * dt
            # Drag / fade for smoke
            if p['type'] == ParticleSystem.SMOKE:
                p['vel'][0] *= 0.98
                p['vel'][1] *= 0.98
                p['size'] = min(p['size'] + 4 * dt, 18)
            alive.append(p)
        self.particles = alive

    def draw(self, surface, camera):
        for p in self.particles:
            sx, sy = camera.world_to_screen(p['pos'])
            alpha_ratio = p['life'] / p['max_life']
            size = max(1, int(p['size'] * alpha_ratio if p['type'] == ParticleSystem.SPARKLE
                              else p['size']))
            # Fade color
            r, g, b = p['color']
            alpha = int(alpha_ratio * 220)
            # Draw with alpha using a temp surface
            if size < 2:
                surface.set_at((int(sx), int(sy)), p['color'])
            else:
                try:
                    tmp = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(tmp, (r, g, b, alpha), (size + 1, size + 1), size)
                    surface.blit(tmp, (int(sx) - size - 1, int(sy) - size - 1))
                except Exception:
                    pass
