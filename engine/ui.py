"""
UI components: Buttons, Health Bars, Status Badges, Tooltips, Top Bar.
"""
import pygame
from settings import (
    COLOR_BG_PANEL, COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED, COLOR_TEXT_GOLD,
    COLOR_HEALTH_RED, COLOR_HEALTH_BG, COLOR_BLOCK_BLUE, COLOR_CARD_BORDER,
    FONTS
)
from engine.sound import play_sfx

class Button:
    def __init__(self, rect, text, font=None, bg_color=(45, 38, 55), hover_color=(75, 60, 95), text_color=COLOR_TEXT_LIGHT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.enabled = True

    def update(self, mouse_pos):
        if not self.enabled:
            self.is_hovered = False
            return False
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                play_sfx('click', 0.5)
                return True
        return False

    def draw(self, surface):
        font = self.font or FONTS['medium']
        color = (35, 30, 40) if not self.enabled else (self.hover_color if self.is_hovered else self.bg_color)
        border_color = (60, 50, 70) if not self.enabled else ((220, 190, 100) if self.is_hovered else COLOR_CARD_BORDER)
        
        # Rounded box
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)

        text_col = (110, 100, 120) if not self.enabled else self.text_color
        rendered = font.render(self.text, True, text_col)
        text_rect = rendered.get_rect(center=self.rect.center)
        surface.blit(rendered, text_rect)

class HealthBar:
    @staticmethod
    def draw(surface, x, y, width, height, current_hp, max_hp, block=0, font=None):
        font = font or FONTS['small']
        
        # Background
        pygame.draw.rect(surface, COLOR_HEALTH_BG, (x, y, width, height), border_radius=4)

        # Health fill
        hp_ratio = max(0.0, min(1.0, current_hp / max(1, max_hp)))
        hp_width = int(width * hp_ratio)
        if hp_width > 0:
            pygame.draw.rect(surface, COLOR_HEALTH_RED, (x, y, hp_width, height), border_radius=4)

        # Block overlay / shield highlight
        if block > 0:
            block_ratio = min(1.0, block / max(1, max_hp))
            block_width = int(width * block_ratio)
            block_surf = pygame.Surface((block_width, height), pygame.SRCALPHA)
            block_surf.fill((*COLOR_BLOCK_BLUE, 200))
            surface.blit(block_surf, (x, y))

        # Border
        pygame.draw.rect(surface, (80, 60, 90), (x, y, width, height), width=1, border_radius=4)

        # Text: HP (and Block if > 0)
        hp_str = f"{current_hp}/{max_hp}"
        if block > 0:
            hp_str += f" (+{block})"
        txt = font.render(hp_str, True, COLOR_TEXT_LIGHT)
        txt_rect = txt.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(txt, txt_rect)

        # Shield icon on the left if block > 0
        if block > 0:
            shield_size = 18
            sx = x - shield_size - 4
            sy = y + (height - shield_size) // 2
            pygame.draw.polygon(surface, COLOR_BLOCK_BLUE, [
                (sx + shield_size // 2, sy),
                (sx + shield_size, sy + shield_size // 3),
                (sx + shield_size // 2, sy + shield_size),
                (sx, sy + shield_size // 3)
            ])
            pygame.draw.polygon(surface, (255, 255, 255), [
                (sx + shield_size // 2, sy),
                (sx + shield_size, sy + shield_size // 3),
                (sx + shield_size // 2, sy + shield_size),
                (sx, sy + shield_size // 3)
            ], 1)

def draw_top_bar(surface, player, current_floor, screen_width=1280):
    """Draw top header with Player stats, Floor, Gold, Potions, and Relics."""
    bar_rect = pygame.Rect(0, 0, screen_width, 50)
    pygame.draw.rect(surface, (20, 16, 26), bar_rect)
    pygame.draw.line(surface, (60, 50, 75), (0, 50), (screen_width, 50), 2)

    # Floor counter
    floor_txt = FONTS['bold'].render(f"FLOOR {current_floor}", True, (200, 190, 220))
    surface.blit(floor_txt, (20, 14))

    # Player HP
    hp_txt = FONTS['bold'].render(f"HP {player.hp}/{player.max_hp}", True, COLOR_HEALTH_RED)
    surface.blit(hp_txt, (140, 14))

    # Gold
    gold_txt = FONTS['bold'].render(f"{player.gold} Gold", True, COLOR_TEXT_GOLD)
    surface.blit(gold_txt, (270, 14))

    # Relics list
    rx = 400
    for relic in player.relics:
        relic_rect = pygame.Rect(rx, 8, 34, 34)
        pygame.draw.rect(surface, (45, 35, 60), relic_rect, border_radius=6)
        pygame.draw.rect(surface, (190, 150, 70), relic_rect, width=1, border_radius=6)
        
        # Relic icon letter
        initial = FONTS['bold'].render(relic.name[0], True, (255, 230, 120))
        surface.blit(initial, initial.get_rect(center=relic_rect.center))
        rx += 40

    # Potions list
    px = 850
    for i, potion in enumerate(player.potions):
        p_rect = pygame.Rect(px + i * 42, 8, 34, 34)
        pygame.draw.rect(surface, (30, 25, 40), p_rect, border_radius=6)
        if potion:
            pygame.draw.circle(surface, potion.color, p_rect.center, 12)
            pygame.draw.rect(surface, (180, 160, 210), p_rect, width=1, border_radius=6)
        else:
            pygame.draw.rect(surface, (60, 50, 70), p_rect, width=1, border_radius=6)
