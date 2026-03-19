import pygame
import math
import random
from engine.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class WeatherSystem:
    CLEAR = 0
    CLOUDY = 1
    RAINY = 2
    STORM = 3

    TRANSITION_TIMES = {
        CLEAR: 30.0,
        CLOUDY: 20.0,
        RAINY: 15.0,
        STORM: 10.0,
    }

    def __init__(self):
        self.state = WeatherSystem.CLEAR
        self.state_timer = 0.0
        self.fog_alpha = 0
        self.lightning_flash = 0.0
        self.lightning_timer = random.uniform(3.0, 8.0)

        # Rain particles
        self.rain_particles = []
        self._init_rain()

    def _init_rain(self):
        self.rain_particles = []
        for _ in range(300):
            self.rain_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(400, 700),
                'length': random.randint(10, 20),
            })

    def update(self, dt):
        self.state_timer += dt

        # Transition logic
        next_state_time = self.TRANSITION_TIMES.get(self.state, 20.0)
        if self.state_timer >= next_state_time:
            self.state_timer = 0.0
            self._advance_state()

        # Fog alpha
        target_fog = {
            WeatherSystem.CLEAR: 0,
            WeatherSystem.CLOUDY: 60,
            WeatherSystem.RAINY: 80,
            WeatherSystem.STORM: 40,
        }.get(self.state, 0)
        if self.fog_alpha < target_fog:
            self.fog_alpha = min(self.fog_alpha + 30 * dt, target_fog)
        else:
            self.fog_alpha = max(self.fog_alpha - 30 * dt, target_fog)

        # Rain particles
        if self.state in (WeatherSystem.RAINY, WeatherSystem.STORM):
            for p in self.rain_particles:
                p['y'] += p['speed'] * dt
                p['x'] += 60 * dt
                if p['y'] > SCREEN_HEIGHT:
                    p['y'] = random.randint(-20, 0)
                    p['x'] = random.randint(0, SCREEN_WIDTH)

        # Lightning
        if self.state == WeatherSystem.STORM:
            self.lightning_timer -= dt
            if self.lightning_timer <= 0:
                self.lightning_flash = 0.3
                self.lightning_timer = random.uniform(2.0, 6.0)
        if self.lightning_flash > 0:
            self.lightning_flash = max(0.0, self.lightning_flash - dt * 3.0)

    def _advance_state(self):
        cycle = [WeatherSystem.CLEAR, WeatherSystem.CLOUDY,
                 WeatherSystem.RAINY, WeatherSystem.STORM,
                 WeatherSystem.RAINY, WeatherSystem.CLOUDY]
        try:
            idx = cycle.index(self.state)
        except ValueError:
            idx = 0
        # Small random chance to skip or loop
        if random.random() < 0.3:
            self.state = WeatherSystem.CLEAR
        else:
            self.state = cycle[(idx + 1) % len(cycle)]

    def draw(self, surface):
        # Fog / cloud overlay
        if self.fog_alpha > 0:
            fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fog.fill((180, 200, 220, int(self.fog_alpha)))
            surface.blit(fog, (0, 0))

        # Rain
        if self.state in (WeatherSystem.RAINY, WeatherSystem.STORM):
            for p in self.rain_particles:
                end_x = int(p['x'] + p['length'] * 0.15)
                end_y = int(p['y'] + p['length'])
                alpha = 160 if self.state == WeatherSystem.STORM else 100
                pygame.draw.line(surface, (180, 200, 255, alpha),
                                 (int(p['x']), int(p['y'])), (end_x, end_y), 1)

        # Lightning flash
        if self.lightning_flash > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 240, int(self.lightning_flash * 180)))
            surface.blit(flash, (0, 0))

    def get_wave_modifier(self):
        return {
            WeatherSystem.CLEAR: 1.0,
            WeatherSystem.CLOUDY: 1.2,
            WeatherSystem.RAINY: 1.6,
            WeatherSystem.STORM: 2.5,
        }.get(self.state, 1.0)

    def get_wind_modifier(self):
        return {
            WeatherSystem.CLEAR: 0.8,
            WeatherSystem.CLOUDY: 1.0,
            WeatherSystem.RAINY: 1.2,
            WeatherSystem.STORM: 1.4,
        }.get(self.state, 1.0)

    def get_state_name(self):
        return {
            WeatherSystem.CLEAR: 'Clear',
            WeatherSystem.CLOUDY: 'Cloudy',
            WeatherSystem.RAINY: 'Rain',
            WeatherSystem.STORM: 'Storm',
        }.get(self.state, 'Clear')
