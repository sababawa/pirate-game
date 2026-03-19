import math


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))


def angle_lerp(a, b, t):
    """Lerp angles correctly handling 360/0 wrap-around."""
    diff = (b - a + 180) % 360 - 180
    return a + diff * t


def distance(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def normalize_angle(angle):
    """Returns angle in range 0-360."""
    return angle % 360


def vec2_from_angle(angle_deg):
    """angle 0 = up = (0,-1), angle 90 = right = (1,0)."""
    r = math.radians(angle_deg)
    return (math.sin(r), -math.cos(r))


def angle_from_vec2(vec):
    """Returns degrees from a (dx, dy) vector. 0=up, 90=right."""
    return math.degrees(math.atan2(vec[0], -vec[1])) % 360


def screen_to_world(screen_pos, camera):
    """camera.offset is the world position of the top-left of screen."""
    return (screen_pos[0] + camera.offset.x, screen_pos[1] + camera.offset.y)


def world_to_screen(world_pos, camera):
    """Returns screen coordinates for a world position."""
    return (world_pos[0] - camera.offset.x, world_pos[1] - camera.offset.y)


def smooth_noise_2d(x, y, seed=0):
    def hash2(ix, iy, s):
        n = ix + iy * 57 + s * 131
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

    ix = int(math.floor(x))
    iy = int(math.floor(y))
    fx = x - ix
    fy = y - iy
    ux = fx * fx * (3 - 2 * fx)
    uy = fy * fy * (3 - 2 * fy)
    v00 = hash2(ix, iy, seed)
    v10 = hash2(ix + 1, iy, seed)
    v01 = hash2(ix, iy + 1, seed)
    v11 = hash2(ix + 1, iy + 1, seed)
    return (v00 * (1 - ux) + v10 * ux) * (1 - uy) + (v01 * (1 - ux) + v11 * ux) * uy
