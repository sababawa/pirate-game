import random
import pygame
from world.island import Island
from entities.enemy_ship import EnemyShip
from entities.treasure import Treasure
from engine.settings import WORLD_SIZE
from engine.utils import distance


class WorldGenerator:
    def generate_world(self, seed=42):
        rng = random.Random(seed)
        margin = 800
        world_min = margin
        world_max = WORLD_SIZE - margin

        # --- Islands ---
        islands = []
        attempts = 0
        target_count = rng.randint(15, 20)
        while len(islands) < target_count and attempts < 2000:
            attempts += 1
            x = rng.uniform(world_min, world_max)
            y = rng.uniform(world_min, world_max)
            pos = (x, y)
            # Check min distance from other islands
            too_close = False
            for isl in islands:
                if distance(pos, (isl.pos.x, isl.pos.y)) < 700:
                    too_close = True
                    break
            if too_close:
                continue
            size_cat = rng.choice(['small', 'small', 'medium', 'medium', 'medium', 'large'])
            isl = Island.generate(pos, seed=rng.randint(0, 99999), size_category=size_cat)
            islands.append(isl)

        # --- Sea Rocks ---
        rocks = []
        for _ in range(rng.randint(30, 50)):
            x = rng.uniform(world_min, world_max)
            y = rng.uniform(world_min, world_max)
            pos = (x, y)
            # Avoid island overlap
            on_island = any(distance(pos, (isl.pos.x, isl.pos.y)) < isl.radius + 40
                            for isl in islands)
            if not on_island:
                rocks.append({'pos': pos, 'radius': rng.randint(10, 30)})

        # --- Treasure chests ---
        treasures = []
        tier_pool = ['bronze'] * 10 + ['silver'] * 6 + ['gold'] * 3 + ['legendary'] * 1
        for _ in range(rng.randint(20, 30)):
            x = rng.uniform(world_min, world_max)
            y = rng.uniform(world_min, world_max)
            pos = (x, y)
            on_island = any(distance(pos, (isl.pos.x, isl.pos.y)) < isl.radius + 20
                            for isl in islands)
            if not on_island:
                tier_name = rng.choice(tier_pool)
                tier_map = {'bronze': Treasure.BRONZE, 'silver': Treasure.SILVER,
                            'gold': Treasure.GOLD, 'legendary': Treasure.LEGENDARY}
                treasures.append(Treasure(pygame.math.Vector2(x, y), tier_map[tier_name]))

        # --- Enemy ships ---
        enemy_ships = []
        ship_types = ['sloop'] * 12 + ['galleon'] * 6
        rng.shuffle(ship_types)
        for i in range(min(rng.randint(15, 20), len(ship_types))):
            x = rng.uniform(world_min, world_max)
            y = rng.uniform(world_min, world_max)
            pos = (x, y)
            on_island = any(distance(pos, (isl.pos.x, isl.pos.y)) < isl.radius + 80
                            for isl in islands)
            if not on_island:
                enemy_ships.append(EnemyShip(pygame.math.Vector2(x, y), ship_types[i]))

        return {
            'islands': islands,
            'rocks': rocks,
            'treasures': treasures,
            'enemy_ships': enemy_ships,
        }
