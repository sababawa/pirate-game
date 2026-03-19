import pygame
import sys
import math
from engine.settings import *
from engine.camera import Camera
from engine.utils import *
from world.ocean import OceanRenderer
from world.island import Island
from world.world_gen import WorldGenerator
from world.minimap import Minimap
from world.weather import WeatherSystem
from entities.player_ship import PlayerShip
from entities.enemy_ship import EnemyShip
from entities.treasure import Treasure
from entities.particles import ParticleSystem
from ui.hud import HUD
from ui.menu import MenuSystem
from ui.inventory import Inventory


class Game:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4

    def __init__(self, screen):
        self.screen = screen
        self.state = Game.MENU
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ocean = OceanRenderer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.minimap = Minimap()
        self.weather = WeatherSystem()
        self.particles = ParticleSystem()
        self.hud = HUD()
        self.menu = MenuSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.inventory = Inventory()

        # Day/night
        self.time_of_day = 0.5  # 0=midnight, 0.5=noon, 1=midnight
        self.day_timer = 0.0
        self.day_duration = DAY_CYCLE_MINUTES * 60.0

        # Wind
        self.wind_angle = 45.0
        self.wind_speed = 1.0
        self.wind_change_timer = 0.0

        self._init_world()

    def _init_world(self):
        gen = WorldGenerator()
        world_data = gen.generate_world()
        self.islands = world_data['islands']
        self.rocks = world_data['rocks']
        self.treasures = world_data['treasures']
        self.enemy_ships = world_data['enemy_ships']
        self.cannonballs = []

        # Place player at center
        self.player = PlayerShip(pygame.math.Vector2(WORLD_SIZE // 2, WORLD_SIZE // 2))
        self.camera.offset = pygame.math.Vector2(
            self.player.pos.x - SCREEN_WIDTH // 2,
            self.player.pos.y - SCREEN_HEIGHT // 2
        )

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == Game.MENU:
                action = self.menu.handle_event(event)
                if action == 'start_game':
                    self._start_game()
                elif action == 'quit':
                    pygame.quit()
                    sys.exit()

            elif self.state == Game.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = Game.PAUSED
                        self.menu.state = MenuSystem.PAUSE
                    elif event.key == pygame.K_m:
                        self.minimap.toggle_fullmap()
                    elif event.key == pygame.K_e:
                        self._try_interact()

            elif self.state == Game.PAUSED:
                action = self.menu.handle_event(event)
                if action == 'resume':
                    self.state = Game.PLAYING
                elif action == 'main_menu':
                    self.state = Game.MENU
                    self.menu.state = MenuSystem.MAIN_MENU

            elif self.state in (Game.GAME_OVER, Game.VICTORY):
                action = self.menu.handle_event(event)
                if action == 'sail_again':
                    self._init_world()
                    self._start_game()
                elif action == 'main_menu':
                    self.state = Game.MENU
                    self.menu.state = MenuSystem.MAIN_MENU

        if self.state == Game.PLAYING:
            keys = pygame.key.get_pressed()
            new_balls = self.player.handle_input(keys, events)
            if new_balls:
                self.cannonballs.extend(new_balls)

    def _start_game(self):
        self._init_world()
        self.state = Game.PLAYING
        self.time_of_day = 0.5
        self.day_timer = self.day_duration * 0.5

    def _try_interact(self):
        for treasure in self.treasures:
            if treasure.alive and treasure.can_pickup(self.player.pos):
                self.player.gold += treasure.gold_value
                treasure.alive = False
                self.particles.add_particles(4, (treasure.pos.x, treasure.pos.y), 20)
                if self.player.gold >= VICTORY_GOLD:
                    self.state = Game.VICTORY
                    self.menu.state = MenuSystem.VICTORY
                return

        for island in self.islands:
            if island.has_dock:
                dock_dist = distance(self.player.pos, island.dock_pos)
                if dock_dist < DOCK_REPAIR_RADIUS:
                    self.player.repair(30)
                    return

    def update(self, dt):
        if self.state == Game.MENU:
            self.menu.update(dt)
            return

        if self.state == Game.PAUSED:
            return

        if self.state in (Game.GAME_OVER, Game.VICTORY):
            self.menu.update(dt)
            return

        # Day/night
        self.day_timer += dt
        if self.day_timer >= self.day_duration:
            self.day_timer = 0.0
        self.time_of_day = self.day_timer / self.day_duration

        # Wind
        self.wind_change_timer += dt
        if self.wind_change_timer > 10.0:
            self.wind_change_timer = 0.0
            self.wind_angle += (math.sin(pygame.time.get_ticks() * 0.001) * 15)
            self.wind_angle = normalize_angle(self.wind_angle)

        self.weather.update(dt)
        self.ocean.update(dt)
        self.particles.update(dt)

        # Pass wind info to player for HUD display
        self.player._wind_angle_display = self.wind_angle
        self.player._wind_speed_display = self.wind_speed

        # Update player
        self.player.update(dt, self.wind_angle,
                           self.wind_speed * self.weather.get_wind_modifier(),
                           self.islands, self.rocks)

        # Update camera
        self.camera.update(self.player.pos, dt)

        # Check player death
        if self.player.health <= 0 and self.player.alive:
            self.player.alive = False
            self.state = Game.GAME_OVER
            self.menu.state = MenuSystem.GAME_OVER
            self.camera.add_shake(20)

        # Update enemies
        new_balls = []
        for enemy in self.enemy_ships:
            balls = enemy.update(dt, self.player, self.islands)
            if balls:
                new_balls.extend(balls)
            if not enemy.alive and not enemy.loot_dropped:
                enemy.loot_dropped = True
                loot = enemy.drop_loot()
                self.treasures.extend(loot)
        self.cannonballs.extend(new_balls)

        # Update cannonballs
        for ball in self.cannonballs[:]:
            ball.update(dt, self.islands, self.enemy_ships, self.player)
            if not ball.alive:
                if ball.hit_pos:
                    self.particles.add_particles(0, ball.hit_pos, 15)   # SPLASH
                    if ball.hit_ship:
                        self.camera.add_shake(5)
                        self.particles.add_particles(2, ball.hit_pos, 10)  # EXPLOSION
                self.cannonballs.remove(ball)

        # Update treasures
        for treasure in self.treasures:
            treasure.update(dt)

        # Check dock proximity
        self.player.at_dock = False
        for island in self.islands:
            if island.has_dock:
                if distance(self.player.pos, island.dock_pos) < DOCK_REPAIR_RADIUS:
                    self.player.at_dock = True
                    break

        # Check nearby treasure
        self.player.near_treasure = None
        for treasure in self.treasures:
            if treasure.alive and treasure.can_pickup(self.player.pos):
                self.player.near_treasure = treasure
                break

    def draw(self):
        # 1. Ocean background
        self.ocean.draw(self.screen, self.camera, self.time_of_day)

        # 2. Islands
        for island in self.islands:
            island.draw(self.screen, self.camera)

        # 3. Rocks
        for rock in self.rocks:
            sx, sy = self.camera.world_to_screen(rock['pos'])
            r = rock['radius']
            if -r < sx < SCREEN_WIDTH + r and -r < sy < SCREEN_HEIGHT + r:
                pygame.draw.circle(self.screen, ROCK_COLOR, (int(sx), int(sy)), int(r))
                pygame.draw.circle(self.screen, (80, 80, 90), (int(sx), int(sy)), int(r), 2)

        # 4. Treasures
        for treasure in self.treasures:
            if treasure.alive:
                treasure.draw(self.screen, self.camera)

        # 5. Enemy ships
        for enemy in self.enemy_ships:
            enemy.draw(self.screen, self.camera)

        # 6. Player ship
        self.player.draw(self.screen, self.camera)

        # 7. Cannonballs
        for ball in self.cannonballs:
            ball.draw(self.screen, self.camera)

        # 8. Particles
        self.particles.draw(self.screen, self.camera)

        # 9. Weather overlay
        self.weather.draw(self.screen)

        # 10. HUD
        self.hud.draw(self.screen, self.player, self.weather, self.time_of_day)

        # 11. Minimap
        self.minimap.draw(self.screen, self.player, self.islands, self.enemy_ships, self.treasures)

        # 12. Menu overlay if needed
        if self.state in (Game.PAUSED, Game.GAME_OVER, Game.VICTORY):
            self.menu.draw(self.screen, self.player.gold)
        elif self.state == Game.MENU:
            self.menu.draw(self.screen)
