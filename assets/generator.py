import pygame
import math
from engine.settings import GOLD_COLOR


def get_font(size):
    """Returns a pygame font, trying bold system fonts first."""
    for name in ('impact', 'arial black', 'arialblack', 'arial', 'freesansbold'):
        path = pygame.font.match_font(name)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


def generate_player_ship(size=64):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Hull shadow
    hull_pts = [
        (cx, cy - size // 2 + 4),
        (cx + size // 4, cy - size // 6),
        (cx + size // 4 - 2, cy + size // 3),
        (cx, cy + size // 2 - 4),
        (cx - size // 4 + 2, cy + size // 3),
        (cx - size // 4, cy - size // 6),
    ]
    pygame.draw.polygon(surf, (60, 35, 10), [(x + 2, y + 2) for x, y in hull_pts])
    # Hull body
    pygame.draw.polygon(surf, (139, 90, 43), hull_pts)
    # Hull highlight
    pygame.draw.polygon(surf, (160, 110, 60), hull_pts, 2)

    # Deck planks
    for i in range(-1, 2):
        plank_x = cx + i * (size // 8)
        pygame.draw.line(surf, (110, 70, 30), (plank_x, cy - size // 4), (plank_x, cy + size // 4), 1)

    # Main mast
    mast_r = max(3, size // 16)
    pygame.draw.circle(surf, (80, 50, 20), (cx + 1, cy + 1), mast_r)
    pygame.draw.circle(surf, (100, 65, 25), (cx, cy), mast_r)

    # Main sail
    sail_pts = [
        (cx - size // 4 + 4, cy - size // 8),
        (cx + size // 4 - 4, cy - size // 8),
        (cx + size // 5 - 4, cy + size // 6),
        (cx - size // 5 + 4, cy + size // 6),
    ]
    pygame.draw.polygon(surf, (245, 245, 220), sail_pts)
    pygame.draw.polygon(surf, (200, 200, 180), sail_pts, 1)
    # Sail cross
    pygame.draw.line(surf, (180, 180, 160), (cx, cy - size // 8), (cx, cy + size // 6), 1)

    # Fore sail (front / top of screen)
    fore_pts = [
        (cx - size // 6 + 2, cy - size // 3),
        (cx + size // 6 - 2, cy - size // 3),
        (cx + size // 8, cy - size // 8 - 2),
        (cx - size // 8, cy - size // 8 - 2),
    ]
    pygame.draw.polygon(surf, (235, 235, 210), fore_pts)
    pygame.draw.polygon(surf, (200, 200, 180), fore_pts, 1)

    # Cannons (sides)
    cannon_color = (50, 50, 55)
    for side in (-1, 1):
        for offset_y in (-size // 8, size // 8):
            cx2 = cx + side * (size // 4 - 2)
            cy2 = cy + offset_y
            pygame.draw.rect(surf, cannon_color, (cx2 - 4, cy2 - 2, 8, 4))

    # Bow ornament
    pygame.draw.circle(surf, GOLD_COLOR, (cx, cy - size // 2 + 5), 3)

    return surf


def generate_enemy_ship(size=64, ship_type='sloop'):
    if ship_type == 'galleon':
        size = 80
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Hull shadow
    hull_pts = [
        (cx, cy - size // 2 + 4),
        (cx + size // 4, cy - size // 6),
        (cx + size // 4 - 2, cy + size // 3),
        (cx, cy + size // 2 - 4),
        (cx - size // 4 + 2, cy + size // 3),
        (cx - size // 4, cy - size // 6),
    ]
    if ship_type == 'galleon':
        hull_pts = [
            (cx, cy - size // 2 + 4),
            (cx + size // 3, cy - size // 6),
            (cx + size // 3 - 2, cy + size // 3),
            (cx, cy + size // 2 - 4),
            (cx - size // 3 + 2, cy + size // 3),
            (cx - size // 3, cy - size // 6),
        ]

    pygame.draw.polygon(surf, (40, 10, 10), [(x + 2, y + 2) for x, y in hull_pts])
    hull_color = (90, 20, 20) if ship_type == 'galleon' else (70, 20, 20)
    pygame.draw.polygon(surf, hull_color, hull_pts)
    pygame.draw.polygon(surf, (120, 40, 40), hull_pts, 2)

    # Mast
    mast_r = max(3, size // 16)
    pygame.draw.circle(surf, (60, 30, 10), (cx + 1, cy + 1), mast_r)
    pygame.draw.circle(surf, (80, 45, 15), (cx, cy), mast_r)

    # Dark sail
    sail_color = (180, 30, 30)
    sail_pts = [
        (cx - size // 4 + 4, cy - size // 8),
        (cx + size // 4 - 4, cy - size // 8),
        (cx + size // 5 - 4, cy + size // 6),
        (cx - size // 5 + 4, cy + size // 6),
    ]
    pygame.draw.polygon(surf, sail_color, sail_pts)
    pygame.draw.polygon(surf, (140, 20, 20), sail_pts, 1)
    # Skull crossbones marker
    pygame.draw.circle(surf, (220, 220, 220), (cx, cy + size // 20), 4)

    # Fore sail
    fore_pts = [
        (cx - size // 6 + 2, cy - size // 3),
        (cx + size // 6 - 2, cy - size // 3),
        (cx + size // 8, cy - size // 8 - 2),
        (cx - size // 8, cy - size // 8 - 2),
    ]
    pygame.draw.polygon(surf, (160, 30, 30), fore_pts)

    # Cannons
    cannon_color = (40, 40, 45)
    sides = 2 if ship_type == 'galleon' else 1
    for side in (-1, 1):
        for i in range(sides):
            offset_y = (i - (sides - 1) / 2) * (size // 6)
            cx2 = cx + side * (size // 4 - 2)
            pygame.draw.rect(surf, cannon_color, (cx2 - 4, cy + int(offset_y) - 2, 8, 4))

    return surf


def generate_cannon_ball(size=8):
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    pygame.draw.circle(surf, (30, 30, 35), (cx + 1, cy + 1), size)
    pygame.draw.circle(surf, (55, 55, 60), (cx, cy), size)
    pygame.draw.circle(surf, (80, 80, 85), (cx - 2, cy - 2), size // 3)
    return surf


def generate_treasure_chest(tier='bronze'):
    size = 32
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    colors = {
        'bronze': ((139, 90, 43), (100, 60, 20), (200, 140, 80)),
        'silver': ((192, 192, 192), (140, 140, 140), (230, 230, 230)),
        'gold': ((255, 215, 0), (200, 160, 0), (255, 240, 100)),
        'legendary': ((180, 0, 255), (120, 0, 180), (220, 100, 255)),
    }
    base, dark, light = colors.get(tier, colors['bronze'])

    # Chest body
    pygame.draw.rect(surf, dark, (4, 12, 24, 16))
    pygame.draw.rect(surf, base, (4, 12, 24, 14))
    # Lid
    pygame.draw.rect(surf, base, (4, 6, 24, 8))
    pygame.draw.rect(surf, light, (4, 6, 24, 4))
    # Metal bands
    pygame.draw.rect(surf, (80, 80, 80), (4, 6, 24, 1))
    pygame.draw.rect(surf, (80, 80, 80), (4, 20, 24, 1))
    # Lock
    pygame.draw.rect(surf, (200, 170, 50), (13, 15, 6, 5))
    # Border
    pygame.draw.rect(surf, (60, 40, 10), (4, 6, 24, 22), 1)

    return surf


def generate_island_tree():
    surf = pygame.Surface((20, 24), pygame.SRCALPHA)
    # Trunk
    pygame.draw.rect(surf, (100, 65, 25), (8, 16, 4, 8))
    # Canopy
    pygame.draw.circle(surf, (30, 100, 30), (10, 12), 8)
    pygame.draw.circle(surf, (50, 130, 50), (10, 10), 7)
    return surf


def generate_palm_tree():
    surf = pygame.Surface((24, 28), pygame.SRCALPHA)
    # Trunk (slightly curved)
    for i in range(10):
        x = 12 + i // 3
        pygame.draw.rect(surf, (120, 80, 30), (x, 18 - i, 3, 3))
    # Fronds
    for angle in range(0, 360, 60):
        r = math.radians(angle)
        ex = int(12 + math.cos(r) * 10)
        ey = int(8 + math.sin(r) * 6)
        pygame.draw.line(surf, (50, 140, 40), (12, 8), (ex, ey), 2)
        pygame.draw.circle(surf, (60, 160, 50), (ex, ey), 3)
    return surf


def generate_rock():
    size = 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    pts = []
    for i in range(7):
        a = math.radians(i * 360 / 7)
        r = 7 + math.sin(i * 2.3) * 2
        pts.append((int(cx + math.cos(a) * r), int(cy + math.sin(a) * r)))
    pygame.draw.polygon(surf, (80, 80, 90), pts)
    pygame.draw.polygon(surf, (110, 110, 120), pts, 1)
    pygame.draw.circle(surf, (130, 130, 140), (cx - 2, cy - 2), 2)
    return surf


def generate_building():
    surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    # Walls
    pygame.draw.rect(surf, (180, 150, 100), (2, 6, 20, 16))
    # Roof
    pts = [(2, 6), (12, 1), (22, 6)]
    pygame.draw.polygon(surf, (150, 60, 40), pts)
    # Door
    pygame.draw.rect(surf, (80, 50, 20), (9, 14, 6, 8))
    # Window
    pygame.draw.rect(surf, (200, 220, 255), (4, 9, 5, 5))
    pygame.draw.rect(surf, (100, 80, 50), (4, 9, 5, 5), 1)
    # Border
    pygame.draw.rect(surf, (120, 90, 60), (2, 6, 20, 16), 1)
    return surf


def generate_coin():
    size = 16
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, (180, 140, 0), (size // 2 + 1, size // 2 + 1), size // 2 - 1)
    pygame.draw.circle(surf, (255, 215, 0), (size // 2, size // 2), size // 2 - 1)
    pygame.draw.circle(surf, (255, 240, 100), (size // 2, size // 2), size // 2 - 1, 1)
    font = get_font(10)
    t = font.render('G', True, (180, 130, 0))
    surf.blit(t, (size // 2 - t.get_width() // 2, size // 2 - t.get_height() // 2))
    return surf
