import pygame
import math
import random
from engine.settings import (SAND, GRASS, FOREST, ROCK_COLOR, WOOD_COLOR,
                              SCREEN_WIDTH, SCREEN_HEIGHT)
from engine.utils import smooth_noise_2d
from assets.generator import (generate_island_tree, generate_palm_tree,
                               generate_rock, generate_building)


class Island:
    def __init__(self, pos, seed, size_category='medium'):
        self.pos = pygame.math.Vector2(pos)
        self.seed = seed
        self.size_category = size_category
        self._generate()

    @classmethod
    def generate(cls, pos, seed, size_category='medium'):
        return cls(pos, seed, size_category)

    def _generate(self):
        rng = random.Random(self.seed)

        size_map = {'small': 120, 'medium': 200, 'large': 300}
        self.radius = size_map.get(self.size_category, 200) + rng.randint(-30, 30)

        # Island type
        roll = rng.random()
        if roll < 0.4:
            self.island_type = 'town'
        elif roll < 0.65:
            self.island_type = 'fort'
        else:
            self.island_type = 'wilderness'

        # Coastline polygon
        num_pts = 14
        self.coast_pts = []
        for i in range(num_pts):
            angle = (i / num_pts) * math.pi * 2
            noise_val = smooth_noise_2d(math.cos(angle) * 2, math.sin(angle) * 2, self.seed)
            r = self.radius * (0.82 + noise_val * 0.28)
            self.coast_pts.append((
                self.pos.x + math.cos(angle) * r,
                self.pos.y + math.sin(angle) * r
            ))

        # Beach ring (slightly larger)
        self.beach_pts = []
        for i in range(num_pts):
            angle = (i / num_pts) * math.pi * 2
            noise_val = smooth_noise_2d(math.cos(angle) * 2, math.sin(angle) * 2, self.seed + 1)
            r = self.radius * (0.95 + noise_val * 0.12)
            self.beach_pts.append((
                self.pos.x + math.cos(angle) * r,
                self.pos.y + math.sin(angle) * r
            ))

        # Trees
        self.trees = []
        tree_count = rng.randint(8, 20)
        for _ in range(tree_count):
            angle = rng.uniform(0, math.pi * 2)
            r = rng.uniform(self.radius * 0.2, self.radius * 0.72)
            tx = self.pos.x + math.cos(angle) * r
            ty = self.pos.y + math.sin(angle) * r
            tree_type = 'palm' if self.island_type == 'wilderness' and rng.random() > 0.5 else 'tree'
            self.trees.append({'pos': (tx, ty), 'type': tree_type})

        # Rocks at edges
        self.rocks = []
        rock_count = rng.randint(4, 12)
        for _ in range(rock_count):
            angle = rng.uniform(0, math.pi * 2)
            r = rng.uniform(self.radius * 0.6, self.radius * 0.95)
            rx = self.pos.x + math.cos(angle) * r
            ry = self.pos.y + math.sin(angle) * r
            self.rocks.append({'pos': (rx, ry)})

        # Buildings for town/fort
        self.buildings = []
        if self.island_type in ('town', 'fort'):
            bcount = rng.randint(3, 7) if self.island_type == 'town' else rng.randint(2, 4)
            for _ in range(bcount):
                angle = rng.uniform(0, math.pi * 2)
                r = rng.uniform(self.radius * 0.1, self.radius * 0.45)
                bx = self.pos.x + math.cos(angle) * r
                by = self.pos.y + math.sin(angle) * r
                self.buildings.append({'pos': (bx, by)})

        # Dock
        if self.island_type in ('town', 'fort'):
            dock_angle = rng.uniform(0, math.pi * 2)
            dock_r = self.radius * 0.88
            self.dock_pos = pygame.math.Vector2(
                self.pos.x + math.cos(dock_angle) * dock_r,
                self.pos.y + math.sin(dock_angle) * dock_r
            )
        else:
            self.dock_pos = None

        # Pre-render island surface
        self._render_surf = None
        self._render_surf_offset = None

    @property
    def has_dock(self):
        return self.island_type in ('town', 'fort')

    def _build_surface(self):
        pad = int(self.radius * 1.15) + 20
        size = pad * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = pad, pad

        def to_local(wx, wy):
            return (cx + wx - self.pos.x, cy + wy - self.pos.y)

        beach_local = [to_local(p[0], p[1]) for p in self.beach_pts]
        coast_local = [to_local(p[0], p[1]) for p in self.coast_pts]

        # Water shadow
        shadow_pts = [(x + 4, y + 4) for x, y in beach_local]
        pygame.draw.polygon(surf, (10, 25, 60, 80), shadow_pts)

        # Beach
        pygame.draw.polygon(surf, SAND, beach_local)

        # Grass interior
        pygame.draw.polygon(surf, GRASS, coast_local)

        # Forest center circle
        forest_r = int(self.radius * 0.45)
        pygame.draw.circle(surf, FOREST, (cx, cy), forest_r)

        # Trees
        tree_surf = generate_island_tree()
        palm_surf = generate_palm_tree()
        for tree in self.trees:
            lx, ly = to_local(tree['pos'][0], tree['pos'][1])
            ts = palm_surf if tree['type'] == 'palm' else tree_surf
            surf.blit(ts, (int(lx) - ts.get_width() // 2, int(ly) - ts.get_height() // 2))

        # Rocks
        rock_surf = generate_rock()
        for rock in self.rocks:
            lx, ly = to_local(rock['pos'][0], rock['pos'][1])
            surf.blit(rock_surf, (int(lx) - rock_surf.get_width() // 2,
                                  int(ly) - rock_surf.get_height() // 2))

        # Buildings
        building_surf = generate_building()
        for bld in self.buildings:
            lx, ly = to_local(bld['pos'][0], bld['pos'][1])
            surf.blit(building_surf, (int(lx) - building_surf.get_width() // 2,
                                      int(ly) - building_surf.get_height() // 2))

        # Dock
        if self.has_dock and self.dock_pos:
            dx, dy = to_local(self.dock_pos.x, self.dock_pos.y)
            pygame.draw.rect(surf, WOOD_COLOR, (int(dx) - 8, int(dy) - 4, 16, 8))
            pygame.draw.rect(surf, (100, 65, 20), (int(dx) - 8, int(dy) - 4, 16, 8), 1)

        # Coast outline
        pygame.draw.polygon(surf, (200, 180, 100), beach_local, 2)

        self._render_surf = surf
        self._render_surf_offset = (-pad, -pad)

    def draw(self, surface, camera):
        if self._render_surf is None:
            self._build_surface()

        sx, sy = camera.world_to_screen((self.pos.x, self.pos.y))
        pad = int(self.radius * 1.15) + 20

        # Cull
        if (sx < -pad * 2 or sx > SCREEN_WIDTH + pad * 2 or
                sy < -pad * 2 or sy > SCREEN_HEIGHT + pad * 2):
            return

        surface.blit(self._render_surf,
                     (int(sx) - pad, int(sy) - pad))
