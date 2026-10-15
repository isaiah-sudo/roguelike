"""
Deck View: Full deck inspector overlay.
"""
import pygame
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.ui import Button
from engine.sound import play_sfx
from settings import COLOR_BG_DARK, COLOR_TEXT_LIGHT, FONTS

class DeckView:
    def __init__(self, player):
        self.player = player
        self.close_btn = Button((560, 650, 160, 42), "CLOSE", FONTS['medium'])
        self.hovered_card_idx = -1

    def handle_event(self, event, mouse_pos) -> str:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_btn.handle_event(event):
                return "close_deck"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            play_sfx('click', 0.5)
            return "close_deck"
        return "none"

    def _get_card_rects(self):
        rects = []
        cards_per_row = 6
        start_x = 80
        start_y = 100
        spacing_x = CARD_WIDTH + 24
        spacing_y = CARD_HEIGHT + 24

        for i, card in enumerate(self.player.deck):
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            rects.append((pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), card))
        return rects

    def update(self, dt, mouse_pos):
        self.close_btn.update(mouse_pos)
        self.hovered_card_idx = -1
        for idx, (rect, _) in enumerate(self._get_card_rects()):
            if rect.collidepoint(mouse_pos):
                self.hovered_card_idx = idx
                break

    def draw(self, surface):
        # Dark semi-transparent overlay
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((10, 8, 14, 245))
        surface.blit(overlay, (0, 0))

        title = FONTS['title'].render(f"YOUR DECK ({len(self.player.deck)} Cards)", True, (240, 220, 160))
        surface.blit(title, title.get_rect(center=(640, 50)))

        for idx, (rect, card) in enumerate(self._get_card_rects()):
            draw_card(surface, card, rect.x, rect.y, is_hovered=(idx == self.hovered_card_idx), is_playable=True)

        self.close_btn.draw(surface)
