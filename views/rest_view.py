"""
Rest View: Campfire rest site (Heal 30% Max HP or Smith / Upgrade a Card).
"""
import pygame
import random
from engine.ui import Button, draw_top_bar
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_HEALTH_RED, FONTS
)

class RestView:
    def __init__(self, player):
        self.player = player
        self.rest_btn = Button((380, 480, 240, 60), "REST (+30% HP)", FONTS['medium'], bg_color=(140, 40, 50), hover_color=(180, 50, 65))
        self.smith_btn = Button((660, 480, 240, 60), "SMITH (Upgrade Card)", FONTS['medium'], bg_color=(45, 90, 160), hover_color=(60, 120, 200))
        self.proceed_btn = Button((560, 580, 160, 48), "CONTINUE", FONTS['medium'])
        
        self.action_taken = False
        self.smithing = False
        self.hovered_card_idx = -1
        self.status_message = "The embers crackle in the gloom. Choose your respite."

    def handle_event(self, event, mouse_pos) -> str:
        if self.smithing:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check which card clicked to upgrade
                cards = [c for c in self.player.deck if not c.upgraded]
                card_rects = self._get_smith_card_rects(cards)
                for idx, (rect, card) in enumerate(card_rects):
                    if rect.collidepoint(event.pos):
                        card.upgrade()
                        play_sfx('buff', 0.7)
                        self.action_taken = True
                        self.smithing = False
                        self.status_message = f"Forged {card.name}! The weapon hums with ancient power."
                        break
            return "none"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.action_taken:
                if self.proceed_btn.handle_event(event):
                    return "back_to_map"
                return "none"

            if self.rest_btn.handle_event(event):
                heal_amt = int(self.player.max_hp * 0.3)
                actual_healed = self.player.heal(heal_amt)
                play_sfx('buff', 0.6)
                self.action_taken = True
                self.status_message = f"You rested by the fire and recovered {actual_healed} HP."
                return "none"

            if self.smith_btn.handle_event(event):
                unupgraded = [c for c in self.player.deck if not c.upgraded]
                if unupgraded:
                    self.smithing = True
                    play_sfx('card_draw', 0.5)
                else:
                    self.status_message = "All cards in your deck are already fully upgraded!"
                return "none"

        return "none"

    def _get_smith_card_rects(self, cards):
        rects = []
        cards_per_row = 6
        start_x = 100
        start_y = 150
        spacing_x = CARD_WIDTH + 20
        spacing_y = CARD_HEIGHT + 20

        for i, card in enumerate(cards):
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            rects.append((pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), card))
        return rects

    def update(self, dt, mouse_pos):
        self.rest_btn.update(mouse_pos)
        self.smith_btn.update(mouse_pos)
        self.proceed_btn.update(mouse_pos)

        if self.smithing:
            unupgraded = [c for c in self.player.deck if not c.upgraded]
            card_rects = self._get_smith_card_rects(unupgraded)
            self.hovered_card_idx = -1
            for idx, (rect, _) in enumerate(card_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_card_idx = idx
                    break

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)
        draw_top_bar(surface, self.player, 0)

        if self.smithing:
            title = FONTS['title'].render("SELECT A CARD TO UPGRADE", True, (240, 220, 160))
            surface.blit(title, title.get_rect(center=(640, 100)))

            unupgraded = [c for c in self.player.deck if not c.upgraded]
            card_rects = self._get_smith_card_rects(unupgraded)
            for idx, (rect, card) in enumerate(card_rects):
                draw_card(surface, card, rect.x, rect.y, is_hovered=(idx == self.hovered_card_idx), is_playable=True)
            return

        # Title
        title = FONTS['huge'].render("REST SITE", True, (240, 180, 90))
        surface.blit(title, title.get_rect(center=(640, 140)))

        # Draw Campfire flame art
        fire_center = (640, 310)
        pygame.draw.ellipse(surface, (70, 35, 20), (560, 330, 160, 50))
        # Fire embers
        pygame.draw.polygon(surface, (230, 70, 30), [
            (590, 340), (640, 220), (690, 340), (660, 320), (640, 350), (620, 320)
        ])
        pygame.draw.polygon(surface, (255, 190, 50), [
            (610, 330), (640, 250), (670, 330), (650, 310), (640, 340), (630, 310)
        ])

        # Status text
        msg_surf = FONTS['regular'].render(self.status_message, True, (200, 195, 215))
        surface.blit(msg_surf, msg_surf.get_rect(center=(640, 420)))

        if not self.action_taken:
            self.rest_btn.draw(surface)
            self.smith_btn.draw(surface)
        else:
            self.proceed_btn.draw(surface)
