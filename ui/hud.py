import pygame
import math
from engine.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_MAX_HEALTH,
                              GOLD_COLOR, WHITE, BLACK, RED, GREEN, ORANGE,
                              DARK_GRAY, GRAY)
from assets.generator import get_font, generate_coin
from world.weather import WeatherSystem


_coin_sprite = None


def _get_coin():
    global _coin_sprite
    if _coin_sprite is None:
        _coin_sprite = generate_coin()
    return _coin_sprite


class HUD:
    def __init__(self):
        self._font_sm = None
        self._font_md = None
        self._font_lg = None
        self._initialized = False

    def _init_fonts(self):
        if not self._initialized:
            self._font_sm = get_font(18)
            self._font_md = get_font(22)
            self._font_lg = get_font(28)
            self._initialized = True

    def draw(self, surface, player, weather, time_of_day):
        self._init_fonts()

        # --- Health bar (bottom left) ---
        self._draw_health(surface, player)

        # --- Gold counter (bottom right) ---
        self._draw_gold(surface, player)

        # --- Compass (top left) ---
        self._draw_compass(surface, player)

        # --- Wind arrow ---
        self._draw_wind(surface, player)

        # --- Day / night icon ---
        self._draw_daytime(surface, time_of_day)

        # --- Weather ---
        self._draw_weather(surface, weather)

        # --- Speed ---
        self._draw_speed(surface, player)

        # --- Interaction hints ---
        self._draw_hints(surface, player)

        # --- Low health vignette ---
        if player.health < PLAYER_MAX_HEALTH * 0.3:
            self._draw_vignette(surface, player)

    def _draw_panel(self, surface, rect, alpha=180):
        panel = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        panel.fill((10, 15, 30, alpha))
        surface.blit(panel, (rect[0], rect[1]))
        pygame.draw.rect(surface, (80, 100, 150), rect, 1)

    def _draw_health(self, surface, player):
        bx, by = 20, SCREEN_HEIGHT - 70
        bar_w, bar_h = 200, 22
        self._draw_panel(surface, (bx - 5, by - 20, bar_w + 10, bar_h + 30))

        label = self._font_sm.render('HULL', True, (180, 200, 255))
        surface.blit(label, (bx, by - 18))

        ratio = max(0, player.health) / player.max_health
        bar_color = GREEN if ratio > 0.6 else (220, 180, 0) if ratio > 0.3 else RED

        pygame.draw.rect(surface, (40, 10, 10), (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, bar_color, (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, (150, 170, 200), (bx, by, bar_w, bar_h), 1)

        hp_text = self._font_sm.render(f'{max(0, player.health)}/{player.max_health}', True, WHITE)
        surface.blit(hp_text, (bx + bar_w // 2 - hp_text.get_width() // 2, by + 3))

    def _draw_gold(self, surface, player):
        coin = _get_coin()
        gold_str = f'{player.gold:,}'
        text = self._font_md.render(gold_str, True, GOLD_COLOR)
        tw = text.get_width()
        panel_w = tw + 40
        px = SCREEN_WIDTH - panel_w - 20
        py = SCREEN_HEIGHT - 55
        self._draw_panel(surface, (px, py, panel_w, 40))
        surface.blit(coin, (px + 8, py + 12))
        surface.blit(text, (px + 28, py + 10))

    def _draw_compass(self, surface, player):
        cx, cy = 60, 60
        r = 36
        self._draw_panel(surface, (cx - r - 5, cy - r - 5, (r + 5) * 2, (r + 5) * 2), 160)
        pygame.draw.circle(surface, (20, 30, 60), (cx, cy), r)
        pygame.draw.circle(surface, (80, 100, 160), (cx, cy), r, 2)

        # Cardinal letters
        for label, angle in (('N', 0), ('E', 90), ('S', 180), ('W', 270)):
            lx = cx + int(math.sin(math.radians(angle)) * (r - 10))
            ly = cy - int(math.cos(math.radians(angle)) * (r - 10))
            col = RED if label == 'N' else (180, 200, 255)
            t = self._font_sm.render(label, True, col)
            surface.blit(t, (lx - t.get_width() // 2, ly - t.get_height() // 2))

        # Needle
        na = math.radians(player.angle)
        nx = int(math.sin(na) * (r - 14))
        ny = -int(math.cos(na) * (r - 14))
        pygame.draw.line(surface, RED, (cx, cy), (cx + nx, cy + ny), 2)
        pygame.draw.line(surface, (200, 200, 255), (cx, cy), (cx - nx // 2, cy - ny // 2), 2)
        pygame.draw.circle(surface, WHITE, (cx, cy), 3)

    def _draw_wind(self, surface, player):
        # Wind info stored on game via player – we read wind_angle from player if available
        wind_angle = getattr(player, '_wind_angle_display', 45.0)
        wind_speed = getattr(player, '_wind_speed_display', 1.0)

        wx, wy = 60, 145
        r = 22
        self._draw_panel(surface, (wx - r - 5, wy - r - 5, (r + 5) * 2, (r + 5) * 2 + 14), 160)

        pygame.draw.circle(surface, (20, 30, 60), (wx, wy), r)
        pygame.draw.circle(surface, (60, 80, 130), (wx, wy), r, 1)

        wa = math.radians(wind_angle)
        ex = int(math.sin(wa) * (r - 6))
        ey = -int(math.cos(wa) * (r - 6))
        pygame.draw.line(surface, (100, 200, 255), (wx, wy), (wx + ex, wy + ey), 2)
        # Arrowhead
        head_pts = [
            (wx + ex, wy + ey),
            (wx + ex - int(math.cos(wa) * 6) - int(math.sin(wa) * 4),
             wy + ey - int(-math.sin(wa) * 6) - int(math.cos(wa) * 4)),
            (wx + ex - int(math.cos(wa) * 6) + int(math.sin(wa) * 4),
             wy + ey - int(-math.sin(wa) * 6) + int(math.cos(wa) * 4)),
        ]
        pygame.draw.polygon(surface, (100, 200, 255), head_pts)

        wlabel = self._font_sm.render('WIND', True, (180, 200, 255))
        surface.blit(wlabel, (wx - wlabel.get_width() // 2, wy + r + 2))

    def _draw_daytime(self, surface, time_of_day):
        # 0/1=midnight, 0.5=noon
        dx, dy = SCREEN_WIDTH - 50, 50
        is_day = 0.2 < time_of_day < 0.8
        color = (255, 220, 50) if is_day else (200, 220, 255)
        pygame.draw.circle(surface, color, (dx, dy), 16)
        if not is_day:
            # Moon crescent
            pygame.draw.circle(surface, (20, 30, 70), (dx + 6, dy - 4), 13)

        # Day progress arc
        angle_start = -math.pi / 2
        arc_angle = time_of_day * 2 * math.pi
        try:
            arc_rect = pygame.Rect(dx - 20, dy - 20, 40, 40)
            pygame.draw.arc(surface, (255, 200, 50) if is_day else (150, 160, 220),
                            arc_rect, angle_start, angle_start + arc_angle, 2)
        except Exception:
            pass

    def _draw_weather(self, surface, weather):
        state_name = weather.get_state_name()
        wt = self._font_sm.render(state_name, True, (180, 220, 255))
        wx = SCREEN_WIDTH - wt.get_width() - 20
        self._draw_panel(surface, (wx - 4, 80, wt.get_width() + 8, 22), 160)
        surface.blit(wt, (wx, 81))

    def _draw_speed(self, surface, player):
        spd = int(getattr(player, '_current_speed', 0))
        stext = self._font_sm.render(f'{spd} kn', True, (180, 220, 255))
        sx = 20
        sy = SCREEN_HEIGHT - 100
        self._draw_panel(surface, (sx - 4, sy - 2, stext.get_width() + 8, 20), 140)
        surface.blit(stext, (sx, sy))

    def _draw_hints(self, surface, player):
        hints = []
        if player.near_treasure:
            hints.append('E  pick up treasure')
        if player.at_dock:
            hints.append('E  repair at dock')

        if hints:
            y = SCREEN_HEIGHT // 2 + 100
            for hint in hints:
                ht = self._font_md.render(hint, True, GOLD_COLOR)
                hx = SCREEN_WIDTH // 2 - ht.get_width() // 2
                self._draw_panel(surface, (hx - 8, y - 4, ht.get_width() + 16, ht.get_height() + 8), 180)
                surface.blit(ht, (hx, y))
                y += 34

    def _draw_vignette(self, surface, player):
        ratio = player.health / player.max_health
        alpha = int((0.3 - ratio) / 0.3 * 120)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Draw red border
        border = 80
        for i in range(border):
            a = int(alpha * (border - i) / border)
            pygame.draw.rect(vignette, (200, 0, 0, a),
                             (i, i, SCREEN_WIDTH - i * 2, SCREEN_HEIGHT - i * 2), 1)
        surface.blit(vignette, (0, 0))
