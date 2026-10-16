"""
Shop View: Merchant shopkeeper screen with animated lantern lighting,
coin counters, and a fully scrollable Card Removal (Purge) ritual interface with Cancel support.
"""
import pygame
import math
from systems.shop import Shop, ShopItem
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.ui import Button, draw_top_bar, draw_tooltip
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, FONTS
)

class ShopView:
    def __init__(self, shop: Shop, player):
        self.shop = shop
        self.player = player
        self.leave_btn = Button((1080, 642, 160, 46), "LEAVE SHOP", FONTS['medium'], bg_color=(45, 38, 55), hover_color=(75, 60, 95))
        self.remove_card_btn = Button((80, 580, 260, 48), f"Purge Card ({shop.card_removal_cost} Gold)", FONTS['regular'], bg_color=(80, 35, 45), hover_color=(120, 45, 60))
        self.cancel_remove_btn = Button((560, 652, 160, 44), "CANCEL", FONTS['medium'], bg_color=(50, 38, 48), hover_color=(80, 50, 65))
        
        self.removing_card = False
        self.hovered_card_idx = -1
        self.hovered_purge_idx = -1
        self.status_msg = "Welcome, traveler... everything has its price."

        # Scrolling system for card removal
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0
        self.dragging_scrollbar = False
        self.drag_start_mouse_y = 0
        self.drag_start_scroll_y = 0.0

        self.cards_per_row = 6
        self.spacing_x = CARD_WIDTH + 20
        self.spacing_y = CARD_HEIGHT + 24
        self.start_x = (1280 - (self.cards_per_row * self.spacing_x - 20)) // 2
        self.start_y = 120

        self.viewport_top = 105
        self.viewport_bottom = 640
        self.viewport_height = self.viewport_bottom - self.viewport_top

        # Visual animation timer
        self.anim_timer = 0.0

    def _get_max_scroll(self) -> float:
        total_rows = math.ceil(len(self.player.deck) / self.cards_per_row)
        total_content_height = total_rows * self.spacing_y + 30
        if total_content_height <= self.viewport_height:
            return 0.0
        return float(self.viewport_height - total_content_height)

    def _get_deck_rects(self):
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
        if self.removing_card:
            min_scroll = self._get_max_scroll()

            # Mouse wheel
            if event.type == pygame.MOUSEWHEEL:
                self.target_scroll_y += event.y * 55
                self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
                return "none"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.target_scroll_y += 55
                    self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
                    return "none"
                elif event.button == 5:
                    self.target_scroll_y -= 55
                    self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
                    return "none"

                elif event.button == 1:
                    # Cancel purge button
                    if self.cancel_remove_btn.handle_event(event):
                        self.removing_card = False
                        self.scroll_y = 0.0
                        self.target_scroll_y = 0.0
                        return "none"

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
                                rel_y = event.pos[1] - self.viewport_top
                                ratio = max(0.0, min(1.0, rel_y / self.viewport_height))
                                self.target_scroll_y = ratio * min_scroll
                            return "none"

                    # Click a card in deck to purge (within viewport)
                    if self.viewport_top <= event.pos[1] <= self.viewport_bottom:
                        card_rects = self._get_deck_rects()
                        for idx, (rect, card) in enumerate(card_rects):
                            if rect.collidepoint(event.pos):
                                if self.shop.remove_card(self.player, card):
                                    self.status_msg = f"Purged {card.name} from your deck forever."
                                self.removing_card = False
                                self.scroll_y = 0.0
                                self.target_scroll_y = 0.0
                                break
                    return "none"

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_scrollbar = False

            elif event.type == pygame.MOUSEMOTION and self.dragging_scrollbar:
                if min_scroll < 0:
                    delta_y = event.pos[1] - self.drag_start_mouse_y
                    thumb_h = max(40, int(self.viewport_height * (self.viewport_height / (self.viewport_height - min_scroll))))
                    travel = self.viewport_height - thumb_h
                    if travel > 0:
                        delta_scroll = (delta_y / travel) * min_scroll
                        self.target_scroll_y = max(min_scroll, min(0.0, self.drag_start_scroll_y + delta_scroll))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.removing_card = False
                    self.scroll_y = 0.0
                    self.target_scroll_y = 0.0
                    play_sfx('click', 0.5)
                elif event.key == pygame.K_UP:
                    self.target_scroll_y = min(0.0, self.target_scroll_y + 80)
                elif event.key == pygame.K_DOWN:
                    self.target_scroll_y = max(min_scroll, self.target_scroll_y - 80)
            return "none"

        # Normal Shop Events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.leave_btn.handle_event(event):
                return "back_to_map"

            # Remove card service button
            if not self.shop.removal_used and self.remove_card_btn.handle_event(event):
                if self.player.gold >= self.shop.card_removal_cost:
                    self.removing_card = True
                    self.scroll_y = 0.0
                    self.target_scroll_y = 0.0
                    play_sfx('card_draw', 0.5)
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
        y = 125
        for i, item in enumerate(self.shop.cards):
            x = start_x + i * spacing
            rects.append((pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), item))
        return rects

    def _get_shop_relic_rects(self):
        rects = []
        start_x = 420
        y = 440
        for i, item in enumerate(self.shop.relics):
            rects.append((pygame.Rect(start_x + i * 220, y, 190, 72), item))
        return rects

    def _get_shop_potion_rects(self):
        rects = []
        start_x = 420
        y = 540
        for i, item in enumerate(self.shop.potions):
            rects.append((pygame.Rect(start_x + i * 220, y, 190, 62), item))
        return rects

    def update(self, dt, mouse_pos):
        self.anim_timer += dt
        self.leave_btn.update(mouse_pos)
        self.remove_card_btn.update(mouse_pos)

        if self.removing_card:
            self.cancel_remove_btn.update(mouse_pos)
            min_scroll = self._get_max_scroll()
            self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
            self.scroll_y += (self.target_scroll_y - self.scroll_y) * min(1.0, dt * 18.0)

            self.hovered_purge_idx = -1
            if self.viewport_top <= mouse_pos[1] <= self.viewport_bottom:
                for idx, (rect, _) in enumerate(self._get_deck_rects()):
                    if rect.collidepoint(mouse_pos):
                        self.hovered_purge_idx = idx
                        break
        else:
            self.hovered_card_idx = -1
            for idx, (rect, _) in enumerate(self._get_shop_card_rects()):
                if rect.collidepoint(mouse_pos):
                    self.hovered_card_idx = idx
                    break

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        surface.fill(COLOR_BG_DARK)
        draw_top_bar(surface, self.player, 0, mouse_pos=mouse_pos)

        if self.removing_card:
            title = FONTS['title'].render(f"PURGE A CARD FROM YOUR DECK ({len(self.player.deck)} Cards)", True, (255, 110, 110))
            surface.blit(title, title.get_rect(center=(640, 45)))

            sub_hint = FONTS['small'].render("Click any card to permanently banish it into the underworld void. Scroll to view more.", True, (215, 190, 195))
            surface.blit(sub_hint, sub_hint.get_rect(center=(640, 75)))

            pygame.draw.line(surface, (110, 50, 60), (200, 98), (1080, 98), 1)

            # Viewport clipping
            viewport_rect = pygame.Rect(0, self.viewport_top, 1280, self.viewport_height)
            surface.set_clip(viewport_rect)

            for idx, (rect, card) in enumerate(self._get_deck_rects()):
                if rect.bottom >= self.viewport_top and rect.top <= self.viewport_bottom:
                    is_hover = (idx == self.hovered_purge_idx)
                    draw_card(surface, card, rect.x, rect.y, is_hovered=is_hover, is_playable=True)

            surface.set_clip(None)

            # Scrollbar
            min_scroll = self._get_max_scroll()
            if min_scroll < 0:
                track_rect = pygame.Rect(1250, self.viewport_top, 8, self.viewport_height)
                pygame.draw.rect(surface, (30, 24, 40), track_rect, border_radius=4)
                pygame.draw.rect(surface, (70, 55, 80), track_rect, width=1, border_radius=4)

                thumb_h = max(36, int(self.viewport_height * (self.viewport_height / (self.viewport_height - min_scroll))))
                scroll_ratio = (-self.scroll_y) / (-min_scroll)
                thumb_y = self.viewport_top + int((self.viewport_height - thumb_h) * scroll_ratio)
                thumb_rect = pygame.Rect(1249, thumb_y, 10, thumb_h)

                thumb_col = (220, 100, 100) if self.dragging_scrollbar else (170, 80, 90)
                pygame.draw.rect(surface, thumb_col, thumb_rect, border_radius=5)

            # Footer
            footer_surf = pygame.Surface((1280, 80), pygame.SRCALPHA)
            footer_surf.fill((12, 10, 18, 240))
            surface.blit(footer_surf, (0, self.viewport_bottom))
            pygame.draw.line(surface, (110, 50, 60), (200, self.viewport_bottom), (1080, self.viewport_bottom), 1)

            self.cancel_remove_btn.draw(surface)
            return

        # Merchant Banner & Atmospheric Lighting
        # Swinging lantern
        swing = math.sin(self.anim_timer * 2.5) * 6
        lx = 100 + swing
        ly = 150
        # Light glow
        glow_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 200, 60, 30), (80, 80), 75)
        pygame.draw.circle(glow_surf, (255, 220, 100, 45), (80, 80), 40)
        surface.blit(glow_surf, (lx - 80, ly - 80))

        # Lantern chain & body
        pygame.draw.line(surface, (90, 80, 95), (100, 50), (lx, ly - 15), 2)
        pygame.draw.rect(surface, (45, 35, 30), (lx - 12, ly - 15, 24, 30), border_radius=4)
        pygame.draw.rect(surface, (255, 210, 70), (lx - 8, ly - 10, 16, 20), border_radius=2)

        # Hooded Merchant silhouette
        mx = 110
        my = 280
        # Robe
        pygame.draw.polygon(surface, (30, 22, 38), [(mx, my), (mx + 60, my + 140), (mx - 60, my + 140)])
        pygame.draw.circle(surface, (20, 15, 28), (mx, my), 32)
        # Glowing purple eyes under deep hood
        pygame.draw.circle(surface, (190, 80, 255), (mx - 8, my - 2), 3)
        pygame.draw.circle(surface, (190, 80, 255), (mx + 8, my - 2), 3)

        title = FONTS['title'].render("UNDERWORLD MERCHANT", True, COLOR_TEXT_GOLD)
        surface.blit(title, title.get_rect(center=(640, 76)))

        dial_surf = FONTS['regular'].render(f'"{self.status_msg}"', True, (210, 200, 230))
        surface.blit(dial_surf, dial_surf.get_rect(center=(640, 104)))

        # 1. Cards for Sale
        for idx, (rect, item) in enumerate(self._get_shop_card_rects()):
            if not item.purchased:
                is_hov = (idx == self.hovered_card_idx)
                draw_card(surface, item.item, rect.x, rect.y, is_hovered=is_hov, is_playable=True)
                
                # Gold Coin Icon + Price Tag
                price_rect = pygame.Rect(rect.centerx - 45, rect.bottom + 8, 90, 24)
                pygame.draw.rect(surface, (30, 22, 36), price_rect, border_radius=4)
                pygame.draw.rect(surface, (180, 140, 60), price_rect, width=1, border_radius=4)
                pygame.draw.circle(surface, (255, 215, 0), (price_rect.x + 14, price_rect.centery), 6)
                pygame.draw.circle(surface, (200, 150, 0), (price_rect.x + 14, price_rect.centery), 6, 1)

                cost_txt = FONTS['small'].render(f"{item.cost}", True, COLOR_TEXT_GOLD)
                surface.blit(cost_txt, (price_rect.x + 26, price_rect.centery - 8))
            else:
                sold_rect = rect
                pygame.draw.rect(surface, (28, 22, 32), sold_rect, border_radius=10)
                pygame.draw.rect(surface, (60, 50, 70), sold_rect, width=1, border_radius=10)
                sold_txt = FONTS['bold'].render("SOLD", True, (120, 110, 130))
                surface.blit(sold_txt, sold_txt.get_rect(center=sold_rect.center))

        hover_item_tooltip = None

        # 2. Relics for Sale
        for rect, item in self._get_shop_relic_rects():
            if not item.purchased:
                is_hov = rect.collidepoint(mouse_pos)
                pygame.draw.rect(surface, (55, 42, 68) if is_hov else (40, 30, 50), rect, border_radius=8)
                pygame.draw.rect(surface, (255, 215, 80) if is_hov else (190, 150, 70), rect, width=2 if is_hov else 1, border_radius=8)
                r_name = FONTS['bold'].render(item.item.name, True, (255, 230, 140))
                surface.blit(r_name, (rect.x + 12, rect.y + 12))

                # Coin icon + cost
                pygame.draw.circle(surface, (255, 215, 0), (rect.x + 20, rect.y + 48), 6)
                r_cost = FONTS['small'].render(f"{item.cost} Gold", True, COLOR_TEXT_GOLD)
                surface.blit(r_cost, (rect.x + 32, rect.y + 40))

                if is_hov:
                    hover_item_tooltip = (mouse_pos[0], mouse_pos[1] + 15, item.item.name, item.item.description, "SHOP RELIC", (255, 215, 0))
            else:
                pygame.draw.rect(surface, (25, 20, 30), rect, border_radius=8)
                sold_txt = FONTS['regular'].render("SOLD", True, (100, 95, 110))
                surface.blit(sold_txt, sold_txt.get_rect(center=rect.center))

        # 3. Potions for Sale
        for rect, item in self._get_shop_potion_rects():
            if not item.purchased:
                is_hov = rect.collidepoint(mouse_pos)
                pygame.draw.rect(surface, (45, 55, 75) if is_hov else (35, 40, 55), rect, border_radius=8)
                pygame.draw.rect(surface, (140, 200, 255) if is_hov else (100, 160, 200), rect, width=2 if is_hov else 1, border_radius=8)
                p_name = FONTS['bold'].render(item.item.name, True, (160, 220, 255))
                surface.blit(p_name, (rect.x + 12, rect.y + 10))

                pygame.draw.circle(surface, (255, 215, 0), (rect.x + 20, rect.y + 40), 6)
                p_cost = FONTS['small'].render(f"{item.cost} Gold", True, COLOR_TEXT_GOLD)
                surface.blit(p_cost, (rect.x + 32, rect.y + 32))

                if is_hov:
                    hover_item_tooltip = (mouse_pos[0], mouse_pos[1] + 15, item.item.name, item.item.description, "SHOP POTION", (140, 200, 255))
            else:
                pygame.draw.rect(surface, (25, 20, 30), rect, border_radius=8)
                sold_txt = FONTS['regular'].render("SOLD", True, (100, 95, 110))
                surface.blit(sold_txt, sold_txt.get_rect(center=rect.center))

        if hover_item_tooltip:
            draw_tooltip(surface, hover_item_tooltip[0], hover_item_tooltip[1], hover_item_tooltip[2], hover_item_tooltip[3], hover_item_tooltip[4], hover_item_tooltip[5])

        # Card Removal Button
        self.remove_card_btn.text = f"Purge Card ({self.shop.card_removal_cost} Gold)" if not self.shop.removal_used else "Card Purged"
        self.remove_card_btn.enabled = not self.shop.removal_used
        self.remove_card_btn.draw(surface)

        self.leave_btn.draw(surface)
