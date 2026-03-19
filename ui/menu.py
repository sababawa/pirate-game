import pygame
import math
from engine.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GOLD_COLOR, WHITE, BLACK
from assets.generator import get_font


class MenuSystem:
    MAIN_MENU = 0
    PAUSE = 1
    GAME_OVER = 2
    VICTORY = 3

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuSystem.MAIN_MENU
        self.hover_button = -1
        self.ocean_time = 0.0

        self._font_title = None
        self._font_btn = None
        self._font_sub = None
        self._fonts_ready = False

        # Button definitions per state: list of (label, action)
        self._buttons = {
            MenuSystem.MAIN_MENU: [('SET SAIL', 'start_game'), ('QUIT', 'quit')],
            MenuSystem.PAUSE: [('RESUME', 'resume'), ('MAIN MENU', 'main_menu')],
            MenuSystem.GAME_OVER: [('SAIL AGAIN', 'sail_again'), ('MAIN MENU', 'main_menu')],
            MenuSystem.VICTORY: [('SAIL AGAIN', 'sail_again'), ('MAIN MENU', 'main_menu')],
        }

    def _init_fonts(self):
        if not self._fonts_ready:
            self._font_title = get_font(72)
            self._font_btn = get_font(32)
            self._font_sub = get_font(24)
            self._fonts_ready = True

    def update(self, dt):
        self.ocean_time += dt

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_button = -1
            buttons = self._buttons.get(self.state, [])
            rects = self._get_button_rects(len(buttons))
            for i, rect in enumerate(rects):
                if rect.collidepoint(mx, my):
                    self.hover_button = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            buttons = self._buttons.get(self.state, [])
            rects = self._get_button_rects(len(buttons))
            for i, (label, action) in enumerate(buttons):
                if rects[i].collidepoint(mx, my):
                    return action
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                buttons = self._buttons.get(self.state, [])
                if buttons:
                    return buttons[0][1]
            if event.key == pygame.K_ESCAPE:
                if self.state == MenuSystem.PAUSE:
                    return 'resume'
        return None

    def _get_button_rects(self, count):
        btn_w, btn_h = 220, 54
        start_y = self.screen_height // 2 + 40
        rects = []
        for i in range(count):
            bx = self.screen_width // 2 - btn_w // 2
            by = start_y + i * (btn_h + 16)
            rects.append(pygame.Rect(bx, by, btn_w, btn_h))
        return rects

    def draw(self, surface, player_gold=0):
        self._init_fonts()

        if self.state == MenuSystem.MAIN_MENU:
            self._draw_main_menu(surface)
        elif self.state == MenuSystem.PAUSE:
            self._draw_pause(surface)
        elif self.state == MenuSystem.GAME_OVER:
            self._draw_game_over(surface, player_gold)
        elif self.state == MenuSystem.VICTORY:
            self._draw_victory(surface, player_gold)

    def _draw_ocean_bg(self, surface):
        surface.fill((15, 35, 80))
        t = self.ocean_time
        for row in range(0, self.screen_height, 20):
            pts = []
            for x in range(0, self.screen_width + 8, 8):
                y = row + math.sin((x * 0.009) + t * 0.7) * 8
                pts.append((x, int(y)))
            if len(pts) >= 2:
                color_shift = int(math.sin(row * 0.05 + t * 0.3) * 20)
                col = (20 + color_shift, 70, 120)
                pygame.draw.lines(surface, col, False, pts, 2)

    def _draw_button(self, surface, rect, label, hovered):
        bg_color = (40, 60, 100) if hovered else (20, 30, 60)
        border_color = GOLD_COLOR if hovered else (80, 100, 160)
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((*bg_color, 220))
        surface.blit(panel, (rect.x, rect.y))
        pygame.draw.rect(surface, border_color, rect, 2)
        text_col = GOLD_COLOR if hovered else WHITE
        t = self._font_btn.render(label, True, text_col)
        surface.blit(t, (rect.x + rect.width // 2 - t.get_width() // 2,
                         rect.y + rect.height // 2 - t.get_height() // 2))

    def _draw_title(self, surface, text, y, color=GOLD_COLOR, shadow=True):
        if shadow:
            shadow_surf = self._font_title.render(text, True, BLACK)
            surface.blit(shadow_surf, (self.screen_width // 2 - shadow_surf.get_width() // 2 + 4,
                                       y + 4))
        title_surf = self._font_title.render(text, True, color)
        surface.blit(title_surf, (self.screen_width // 2 - title_surf.get_width() // 2, y))

    def _draw_main_menu(self, surface):
        self._draw_ocean_bg(surface)

        # Decorative border
        pygame.draw.rect(surface, GOLD_COLOR, (20, 20, self.screen_width - 40, self.screen_height - 40), 3)
        pygame.draw.rect(surface, (80, 60, 0), (24, 24, self.screen_width - 48, self.screen_height - 48), 1)

        self._draw_title(surface, "PIRATE'S SEA", self.screen_height // 2 - 180)

        sub = self._font_sub.render("Sail the seas, plunder treasures, rule the ocean!", True, (200, 230, 255))
        surface.blit(sub, (self.screen_width // 2 - sub.get_width() // 2, self.screen_height // 2 - 90))

        controls = [
            'W/S - Raise/Lower Sails    A/D - Steer',
            'SPACE - Fire Cannons       E - Interact',
            'M - Toggle Map             ESC - Pause',
            f'Collect {5000:,} gold to win!',
        ]
        cy = self.screen_height // 2 - 50
        for line in controls:
            ct = self._font_sub.render(line, True, (160, 190, 230))
            surface.blit(ct, (self.screen_width // 2 - ct.get_width() // 2, cy))
            cy += 26

        buttons = self._buttons[MenuSystem.MAIN_MENU]
        rects = self._get_button_rects(len(buttons))
        for i, (label, _) in enumerate(buttons):
            self._draw_button(surface, rects[i], label, self.hover_button == i)

    def _draw_pause(self, surface):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self._draw_title(surface, 'PAUSED', self.screen_height // 2 - 160, (200, 200, 255))

        buttons = self._buttons[MenuSystem.PAUSE]
        rects = self._get_button_rects(len(buttons))
        for i, (label, _) in enumerate(buttons):
            self._draw_button(surface, rects[i], label, self.hover_button == i)

    def _draw_game_over(self, surface, gold):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((60, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        self._draw_title(surface, 'YOUR SHIP HAS SUNK', self.screen_height // 2 - 180, (220, 80, 80))

        gold_text = self._font_sub.render(f'Gold collected: {gold:,}', True, GOLD_COLOR)
        surface.blit(gold_text, (self.screen_width // 2 - gold_text.get_width() // 2,
                                  self.screen_height // 2 - 80))

        buttons = self._buttons[MenuSystem.GAME_OVER]
        rects = self._get_button_rects(len(buttons))
        for i, (label, _) in enumerate(buttons):
            self._draw_button(surface, rects[i], label, self.hover_button == i)

    def _draw_victory(self, surface, gold):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((60, 50, 0, 180))
        surface.blit(overlay, (0, 0))

        self._draw_title(surface, 'VICTORY!', self.screen_height // 2 - 180, GOLD_COLOR)

        sub1 = self._font_sub.render('You have plundered the seas!', True, (255, 240, 160))
        surface.blit(sub1, (self.screen_width // 2 - sub1.get_width() // 2, self.screen_height // 2 - 90))

        gold_text = self._font_sub.render(f'Total Gold: {gold:,}', True, GOLD_COLOR)
        surface.blit(gold_text, (self.screen_width // 2 - gold_text.get_width() // 2,
                                  self.screen_height // 2 - 55))

        buttons = self._buttons[MenuSystem.VICTORY]
        rects = self._get_button_rects(len(buttons))
        for i, (label, _) in enumerate(buttons):
            self._draw_button(surface, rects[i], label, self.hover_button == i)
