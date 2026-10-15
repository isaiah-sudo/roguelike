"""
Deck View: Full deck inspector overlay with smooth vertical scrolling,
card type breakdown, scrollbar dragging, and polished dark fantasy framing.
"""
import pygame
import math
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.ui import Button
from engine.sound import play_sfx
from settings import COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, FONTS

class DeckView:
    def __init__(self, player):
        self.player = player
        self.close_btn = Button((560, 652, 160, 44), "CLOSE", FONTS['medium'], bg_color=(45, 38, 55), hover_color=(80, 50, 75))
        self.hovered_card_idx = -1
        
        # Scrolling system
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0
        self.dragging_scrollbar = False
        self.drag_start_mouse_y = 0
        self.drag_start_scroll_y = 0.0
        
        self.cards_per_row = 6
        self.spacing_x = CARD_WIDTH + 20
        self.spacing_y = CARD_HEIGHT + 24
        self.start_x = (1280 - (self.cards_per_row * self.spacing_x - 20)) // 2
        self.start_y = 115
        
        self.viewport_top = 100
        self.viewport_bottom = 640
        self.viewport_height = self.viewport_bottom - self.viewport_top

    def _get_max_scroll(self) -> float:
        total_rows = math.ceil(len(self.player.deck) / self.cards_per_row)
        total_content_height = total_rows * self.spacing_y + 30
        if total_content_height <= self.viewport_height:
            return 0.0
        return float(self.viewport_height - total_content_height)

    def _get_card_rects(self):
        rects = []
        cur_y_offset = int(self.scroll_y)

        for i, card in enumerate(self.player.deck):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            x = self.start_x + col * self.spacing_x
            y = self.start_y + row * self.spacing_y + cur_y_offset
            rects.append((pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), card))
        return rects

    def handle_event(self, event, mouse_pos) -> str:
        min_scroll = self._get_max_scroll()

        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.target_scroll_y += event.y * 55
            self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
            return "none"

        # Legacy / SDL button 4 & 5 scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll Up
                self.target_scroll_y += 55
                self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
                return "none"
            elif event.button == 5:  # Scroll Down
                self.target_scroll_y -= 55
                self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
                return "none"

            elif event.button == 1:
                # Scrollbar track click or drag
                if min_scroll < 0:
                    scrollbar_track = pygame.Rect(1250, self.viewport_top, 12, self.viewport_height)
                    if scrollbar_track.collidepoint(event.pos):
                        thumb_h = max(40, int(self.viewport_height * (self.viewport_height / (self.viewport_height - min_scroll))))
                        scroll_ratio = (-self.scroll_y) / (-min_scroll) if min_scroll < 0 else 0
                        thumb_y = self.viewport_top + int((self.viewport_height - thumb_h) * scroll_ratio)
                        thumb_rect = pygame.Rect(1249, thumb_y, 14, thumb_h)

                        if thumb_rect.collidepoint(event.pos):
                            self.dragging_scrollbar = True
                            self.drag_start_mouse_y = event.pos[1]
                            self.drag_start_scroll_y = self.scroll_y
                        else:
                            # Jump to clicked position
                            rel_y = event.pos[1] - self.viewport_top
                            ratio = max(0.0, min(1.0, rel_y / self.viewport_height))
                            self.target_scroll_y = ratio * min_scroll
                        return "none"

                if self.close_btn.handle_event(event):
                    return "close_deck"

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_scrollbar = False

        elif event.type == pygame.MOUSEMOTION and self.dragging_scrollbar:
            min_scroll = self._get_max_scroll()
            if min_scroll < 0:
                delta_y = event.pos[1] - self.drag_start_mouse_y
                thumb_h = max(40, int(self.viewport_height * (self.viewport_height / (self.viewport_height - min_scroll))))
                travel = self.viewport_height - thumb_h
                if travel > 0:
                    delta_scroll = (delta_y / travel) * min_scroll
                    self.target_scroll_y = max(min_scroll, min(0.0, self.drag_start_scroll_y + delta_scroll))

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_d):
                play_sfx('click', 0.5)
                return "close_deck"
            elif event.key == pygame.K_UP:
                self.target_scroll_y = min(0.0, self.target_scroll_y + 80)
            elif event.key == pygame.K_DOWN:
                self.target_scroll_y = max(min_scroll, self.target_scroll_y - 80)
            elif event.key == pygame.K_PAGEUP:
                self.target_scroll_y = min(0.0, self.target_scroll_y + 300)
            elif event.key == pygame.K_PAGEDOWN:
                self.target_scroll_y = max(min_scroll, self.target_scroll_y - 300)

        return "none"

    def update(self, dt, mouse_pos):
        # Smooth interpolation towards target_scroll_y
        min_scroll = self._get_max_scroll()
        self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * min(1.0, dt * 18.0)

        self.close_btn.update(mouse_pos)
        self.hovered_card_idx = -1

        # Only hover cards that are within the visible viewport
        if self.viewport_top <= mouse_pos[1] <= self.viewport_bottom:
            for idx, (rect, _) in enumerate(self._get_card_rects()):
                if rect.collidepoint(mouse_pos):
                    self.hovered_card_idx = idx
                    break

    def draw(self, surface):
        # Dark semi-transparent overlay
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((10, 8, 16, 246))
        surface.blit(overlay, (0, 0))

        # Title & Deck stats breakdown
        total_cards = len(self.player.deck)
        attacks = sum(1 for c in self.player.deck if getattr(c, 'card_type', None) and c.card_type.value == "Attack")
        skills = sum(1 for c in self.player.deck if getattr(c, 'card_type', None) and c.card_type.value == "Skill")
        powers = sum(1 for c in self.player.deck if getattr(c, 'card_type', None) and c.card_type.value == "Power")
        upgraded = sum(1 for c in self.player.deck if getattr(c, 'upgraded', False))

        title = FONTS['title'].render(f"YOUR DECK ({total_cards} Cards)", True, COLOR_TEXT_GOLD)
        surface.blit(title, title.get_rect(center=(640, 42)))

        stats_str = f"Attacks: {attacks}   •   Skills: {skills}   •   Powers: {powers}   •   Upgraded: {upgraded}"
        stats_surf = FONTS['small'].render(stats_str, True, (190, 180, 205))
        surface.blit(stats_surf, stats_surf.get_rect(center=(640, 74)))

        # Header decorative divider line
        pygame.draw.line(surface, (80, 65, 95), (200, 95), (1080, 95), 1)

        # Set clipping region for cards viewport
        viewport_rect = pygame.Rect(0, self.viewport_top, 1280, self.viewport_height)
        surface.set_clip(viewport_rect)

        # Draw Cards
        for idx, (rect, card) in enumerate(self._get_card_rects()):
            # Only draw visible cards
            if rect.bottom >= self.viewport_top and rect.top <= self.viewport_bottom:
                is_hover = (idx == self.hovered_card_idx)
                draw_card(surface, card, rect.x, rect.y, is_hovered=is_hover, is_playable=True)

        # Reset clipping
        surface.set_clip(None)

        # Draw scrollbar if content exceeds viewport
        min_scroll = self._get_max_scroll()
        if min_scroll < 0:
            track_rect = pygame.Rect(1250, self.viewport_top, 8, self.viewport_height)
            pygame.draw.rect(surface, (30, 24, 40), track_rect, border_radius=4)
            pygame.draw.rect(surface, (70, 55, 80), track_rect, width=1, border_radius=4)

            thumb_h = max(36, int(self.viewport_height * (self.viewport_height / (self.viewport_height - min_scroll))))
            scroll_ratio = (-self.scroll_y) / (-min_scroll)
            thumb_y = self.viewport_top + int((self.viewport_height - thumb_h) * scroll_ratio)
            thumb_rect = pygame.Rect(1249, thumb_y, 10, thumb_h)

            thumb_col = (200, 160, 80) if self.dragging_scrollbar else (140, 110, 170)
            pygame.draw.rect(surface, thumb_col, thumb_rect, border_radius=5)

            # Scroll hint text
            hint_txt = FONTS['small'].render("Scroll: Mouse Wheel / Drag", True, (130, 120, 145))
            surface.blit(hint_txt, (1040, 665))

        # Bottom Bar footer background with gradient glow
        footer_rect = pygame.Rect(0, self.viewport_bottom, 1280, 80)
        footer_surf = pygame.Surface((1280, 80), pygame.SRCALPHA)
        footer_surf.fill((12, 10, 18, 240))
        surface.blit(footer_surf, (0, self.viewport_bottom))
        pygame.draw.line(surface, (80, 65, 95), (200, self.viewport_bottom), (1080, self.viewport_bottom), 1)

        self.close_btn.draw(surface)
