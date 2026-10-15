"""
Shop View: Merchant shopkeeper screen.
"""
import pygame
from systems.shop import Shop, ShopItem
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.ui import Button, draw_top_bar
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, FONTS
)

class ShopView:
    def __init__(self, shop: Shop, player):
        self.shop = shop
        self.player = player
        self.leave_btn = Button((1080, 640, 160, 45), "LEAVE SHOP", FONTS['medium'])
        self.remove_card_btn = Button((80, 580, 260, 48), f"Remove Card ({shop.card_removal_cost} Gold)", FONTS['regular'], bg_color=(80, 35, 45))
        
        self.removing_card = False
        self.hovered_card_idx = -1
        self.status_msg = "Welcome, traveler... everything has its price."

    def handle_event(self, event, mouse_pos) -> str:
        if self.removing_card:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Click a card in deck to purge
                card_rects = self._get_deck_rects()
                for idx, (rect, card) in enumerate(card_rects):
                    if rect.collidepoint(event.pos):
                        if self.shop.remove_card(self.player, card):
                            self.status_msg = f"Purged {card.name} from your deck forever."
                        self.removing_card = False
                        break
            return "none"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.leave_btn.handle_event(event):
                return "back_to_map"

            # Remove card service button
            if not self.shop.removal_used and self.remove_card_btn.handle_event(event):
                if self.player.gold >= self.shop.card_removal_cost:
                    self.removing_card = True
                else:
                    self.status_msg = "You cannot afford the purge ritual!"
                return "none"

            # Check buying cards
            card_rects = self._get_shop_card_rects()
            for idx, (rect, item) in enumerate(card_rects):
                if rect.collidepoint(event.pos) and not item.purchased:
                    if self.shop.buy_card(self.player, item):
                        self.status_msg = f"Purchased {item.item.name}!"
                    else:
                        self.status_msg = "Not enough gold!"
                    return "none"

            # Check buying relics
            relic_rects = self._get_shop_relic_rects()
            for idx, (rect, item) in enumerate(relic_rects):
                if rect.collidepoint(event.pos) and not item.purchased:
                    if self.shop.buy_relic(self.player, item):
                        self.status_msg = f"Purchased {item.item.name}!"
                    else:
                        self.status_msg = "Not enough gold!"
                    return "none"

            # Check buying potions
            pot_rects = self._get_shop_potion_rects()
            for idx, (rect, item) in enumerate(pot_rects):
                if rect.collidepoint(event.pos) and not item.purchased:
                    if self.shop.buy_potion(self.player, item):
                        self.status_msg = f"Purchased {item.item.name}!"
                    else:
                        self.status_msg = "Not enough gold or potion slots full!"
                    return "none"

        return "none"

    def _get_shop_card_rects(self):
        rects = []
        spacing = 190
        start_x = 180
        y = 120
        for i, item in enumerate(self.shop.cards):
            x = start_x + i * spacing
            rects.append((pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), item))
        return rects

    def _get_shop_relic_rects(self):
        rects = []
        start_x = 420
        y = 440
        for i, item in enumerate(self.shop.relics):
            rects.append((pygame.Rect(start_x + i * 220, y, 180, 70), item))
        return rects

    def _get_shop_potion_rects(self):
        rects = []
        start_x = 420
        y = 540
        for i, item in enumerate(self.shop.potions):
            rects.append((pygame.Rect(start_x + i * 220, y, 180, 60), item))
        return rects

    def _get_deck_rects(self):
        rects = []
        cards_per_row = 6
        start_x = 100
        start_y = 140
        for i, card in enumerate(self.player.deck):
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * (CARD_WIDTH + 20)
            y = start_y + row * (CARD_HEIGHT + 20)
            rects.append((pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), card))
        return rects

    def update(self, dt, mouse_pos):
        self.leave_btn.update(mouse_pos)
        self.remove_card_btn.update(mouse_pos)

        if not self.removing_card:
            self.hovered_card_idx = -1
            for idx, (rect, _) in enumerate(self._get_shop_card_rects()):
                if rect.collidepoint(mouse_pos):
                    self.hovered_card_idx = idx
                    break

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)
        draw_top_bar(surface, self.player, 0)

        if self.removing_card:
            title = FONTS['title'].render("SELECT A CARD TO REMOVE FROM DECK", True, (240, 100, 100))
            surface.blit(title, title.get_rect(center=(640, 90)))
            for rect, card in self._get_deck_rects():
                draw_card(surface, card, rect.x, rect.y, is_playable=True)
            return

        # Merchant Banner
        title = FONTS['title'].render("UNDERWORLD MERCHANT", True, COLOR_TEXT_GOLD)
        surface.blit(title, title.get_rect(center=(640, 80)))

        # Status dialogue
        dial_surf = FONTS['regular'].render(f'"{self.status_msg}"', True, (200, 190, 220))
        surface.blit(dial_surf, dial_surf.get_rect(center=(640, 105)))

        # 1. Cards for Sale
        for idx, (rect, item) in enumerate(self._get_shop_card_rects()):
            if not item.purchased:
                draw_card(surface, item.item, rect.x, rect.y, is_hovered=(idx == self.hovered_card_idx), is_playable=True)
                cost_txt = FONTS['bold'].render(f"{item.cost} Gold", True, COLOR_TEXT_GOLD)
                surface.blit(cost_txt, cost_txt.get_rect(center=(rect.centerx, rect.bottom + 16)))
            else:
                sold_rect = rect
                pygame.draw.rect(surface, (30, 25, 35), sold_rect, border_radius=10)
                pygame.draw.rect(surface, (70, 60, 80), sold_rect, width=1, border_radius=10)
                sold_txt = FONTS['bold'].render("SOLD", True, (130, 120, 140))
                surface.blit(sold_txt, sold_txt.get_rect(center=sold_rect.center))

        # 2. Relics for Sale
        for rect, item in self._get_shop_relic_rects():
            if not item.purchased:
                pygame.draw.rect(surface, (40, 30, 50), rect, border_radius=8)
                pygame.draw.rect(surface, (180, 140, 70), rect, width=1, border_radius=8)
                r_name = FONTS['bold'].render(item.item.name, True, (255, 230, 140))
                surface.blit(r_name, (rect.x + 10, rect.y + 10))
                r_cost = FONTS['small'].render(f"{item.cost} Gold", True, COLOR_TEXT_GOLD)
                surface.blit(r_cost, (rect.x + 10, rect.y + 38))
            else:
                pygame.draw.rect(surface, (25, 20, 30), rect, border_radius=8)
                sold_txt = FONTS['regular'].render("SOLD", True, (100, 95, 110))
                surface.blit(sold_txt, sold_txt.get_rect(center=rect.center))

        # 3. Potions for Sale
        for rect, item in self._get_shop_potion_rects():
            if not item.purchased:
                pygame.draw.rect(surface, (35, 40, 55), rect, border_radius=8)
                pygame.draw.rect(surface, (100, 160, 200), rect, width=1, border_radius=8)
                p_name = FONTS['bold'].render(item.item.name, True, (160, 220, 255))
                surface.blit(p_name, (rect.x + 10, rect.y + 8))
                p_cost = FONTS['small'].render(f"{item.cost} Gold", True, COLOR_TEXT_GOLD)
                surface.blit(p_cost, (rect.x + 10, rect.y + 34))
            else:
                pygame.draw.rect(surface, (25, 20, 30), rect, border_radius=8)
                sold_txt = FONTS['regular'].render("SOLD", True, (100, 95, 110))
                surface.blit(sold_txt, sold_txt.get_rect(center=rect.center))

        # Card Removal Button
        self.remove_card_btn.text = f"Purge Card ({self.shop.card_removal_cost} Gold)" if not self.shop.removal_used else "Card Purged"
        self.remove_card_btn.enabled = not self.shop.removal_used
        self.remove_card_btn.draw(surface)

        self.leave_btn.draw(surface)
