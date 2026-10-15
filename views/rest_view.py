"""
Rest View: Campfire rest site (Heal 30% Max HP or Smith / Upgrade a Card).
Features animated atmospheric campfire with dancing flame tongues and rising embers,
plus a full scrollable card upgrade interface with scrollbar and Cancel option.
"""
import pygame
import math
import random
from engine.ui import Button, draw_top_bar
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_HEALTH_RED, COLOR_TEXT_GOLD, FONTS
)

class RestView:
    def __init__(self, player):
        self.player = player
        self.rest_btn = Button((380, 490, 240, 58), "REST (+30% HP)", FONTS['medium'], bg_color=(140, 40, 50), hover_color=(180, 50, 65))
        self.smith_btn = Button((660, 490, 240, 58), "SMITH (Upgrade Card)", FONTS['medium'], bg_color=(45, 90, 160), hover_color=(60, 120, 200))
        self.proceed_btn = Button((560, 580, 160, 48), "CONTINUE", FONTS['medium'])
        self.cancel_smith_btn = Button((560, 652, 160, 44), "CANCEL", FONTS['medium'], bg_color=(50, 38, 48), hover_color=(80, 50, 65))
        
        self.action_taken = False
        self.smithing = False
        self.hovered_card_idx = -1
        self.status_message = "The embers crackle in the gloom. Choose your respite."

        # Scrolling system for smithing
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

        # Campfire animated embers
        self.embers = []
        self.flame_timer = 0.0

    def _get_unupgraded_cards(self):
        return [c for c in self.player.deck if not getattr(c, 'upgraded', False)]

    def _get_max_scroll(self, cards) -> float:
        total_rows = math.ceil(len(cards) / self.cards_per_row)
        total_content_height = total_rows * self.spacing_y + 30
        if total_content_height <= self.viewport_height:
            return 0.0
        return float(self.viewport_height - total_content_height)

    def _get_smith_card_rects(self, cards):
        rects = []
        cur_y_offset = int(self.scroll_y)

        for i, card in enumerate(cards):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            x = self.start_x + col * self.spacing_x
            y = self.start_y + row * self.spacing_y + cur_y_offset
            rects.append((pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), card))
        return rects

    def handle_event(self, event, mouse_pos) -> str:
        if self.smithing:
            cards = self._get_unupgraded_cards()
            min_scroll = self._get_max_scroll(cards)

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
                    # Cancel button
                    if self.cancel_smith_btn.handle_event(event):
                        self.smithing = False
                        self.scroll_y = 0.0
                        self.target_scroll_y = 0.0
                        return "none"

                    # Scrollbar track
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

                    # Check which card clicked to upgrade (only within viewport)
                    if self.viewport_top <= event.pos[1] <= self.viewport_bottom:
                        card_rects = self._get_smith_card_rects(cards)
                        for idx, (rect, card) in enumerate(card_rects):
                            if rect.collidepoint(event.pos):
                                card.upgrade()
                                play_sfx('buff', 0.7)
                                self.action_taken = True
                                self.smithing = False
                                self.scroll_y = 0.0
                                self.target_scroll_y = 0.0
                                self.status_message = f"Forged {card.name}! The weapon hums with ancient power."
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
                    self.smithing = False
                    self.scroll_y = 0.0
                    self.target_scroll_y = 0.0
                    play_sfx('click', 0.5)
                elif event.key == pygame.K_UP:
                    self.target_scroll_y = min(0.0, self.target_scroll_y + 80)
                elif event.key == pygame.K_DOWN:
                    self.target_scroll_y = max(min_scroll, self.target_scroll_y - 80)
            return "none"

        # Main Campfire Actions
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
                unupgraded = self._get_unupgraded_cards()
                if unupgraded:
                    self.smithing = True
                    self.scroll_y = 0.0
                    self.target_scroll_y = 0.0
                    play_sfx('card_draw', 0.5)
                else:
                    self.status_message = "All cards in your deck are already fully upgraded!"
                return "none"

        return "none"

    def update(self, dt, mouse_pos):
        self.flame_timer += dt

        # Spawn campfire embers
        if not self.smithing and random.random() < 0.45:
            # Spawn near fire center (640, 340)
            self.embers.append([
                640 + random.uniform(-40, 40),
                335 + random.uniform(-10, 10),
                random.uniform(-0.6, 0.6),
                random.uniform(-1.8, -0.8),
                random.uniform(0.6, 1.4),
                random.uniform(2.0, 4.5),
                random.choice([(255, 180, 50), (255, 100, 30), (255, 230, 90)])
            ])

        for e in self.embers:
            e[0] += e[2]
            e[1] += e[3]
            e[4] -= dt
        self.embers = [e for e in self.embers if e[4] > 0]

        if self.smithing:
            self.cancel_smith_btn.update(mouse_pos)
            unupgraded = self._get_unupgraded_cards()
            min_scroll = self._get_max_scroll(unupgraded)
            self.target_scroll_y = max(min_scroll, min(0.0, self.target_scroll_y))
            self.scroll_y += (self.target_scroll_y - self.scroll_y) * min(1.0, dt * 18.0)

            card_rects = self._get_smith_card_rects(unupgraded)
            self.hovered_card_idx = -1
            if self.viewport_top <= mouse_pos[1] <= self.viewport_bottom:
                for idx, (rect, _) in enumerate(card_rects):
                    if rect.collidepoint(mouse_pos):
                        self.hovered_card_idx = idx
                        break
        else:
            self.rest_btn.update(mouse_pos)
            self.smith_btn.update(mouse_pos)
            self.proceed_btn.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)
        draw_top_bar(surface, self.player, 0)

        if self.smithing:
            # Header
            unupgraded = self._get_unupgraded_cards()
            title = FONTS['title'].render(f"SELECT A CARD TO UPGRADE ({len(unupgraded)} Available)", True, COLOR_TEXT_GOLD)
            surface.blit(title, title.get_rect(center=(640, 45)))

            sub_hint = FONTS['small'].render("Click any card to forge and master its true potential. Scroll to view more.", True, (190, 180, 205))
            surface.blit(sub_hint, sub_hint.get_rect(center=(640, 75)))

            pygame.draw.line(surface, (80, 65, 95), (200, 98), (1080, 98), 1)

            # Viewport clipping
            viewport_rect = pygame.Rect(0, self.viewport_top, 1280, self.viewport_height)
            surface.set_clip(viewport_rect)

            card_rects = self._get_smith_card_rects(unupgraded)
            for idx, (rect, card) in enumerate(card_rects):
                if rect.bottom >= self.viewport_top and rect.top <= self.viewport_bottom:
                    is_hover = (idx == self.hovered_card_idx)
                    draw_card(surface, card, rect.x, rect.y, is_hovered=is_hover, is_playable=True)

            surface.set_clip(None)

            # Scrollbar
            min_scroll = self._get_max_scroll(unupgraded)
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

            # Footer
            footer_surf = pygame.Surface((1280, 80), pygame.SRCALPHA)
            footer_surf.fill((12, 10, 18, 240))
            surface.blit(footer_surf, (0, self.viewport_bottom))
            pygame.draw.line(surface, (80, 65, 95), (200, self.viewport_bottom), (1080, self.viewport_bottom), 1)

            self.cancel_smith_btn.draw(surface)
            return

        # Main Campfire Screen
        title = FONTS['huge'].render("CAMPFIRE REST SITE", True, (245, 190, 95))
        surface.blit(title, title.get_rect(center=(640, 125)))

        # Pulsing warm radial light around campfire
        pulse = math.sin(self.flame_timer * 4.0) * 8
        glow_radius = int(140 + pulse)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (240, 110, 25, 30), (glow_radius, glow_radius), glow_radius)
        pygame.draw.circle(glow_surf, (255, 170, 40, 45), (glow_radius, glow_radius), int(glow_radius * 0.65))
        pygame.draw.circle(glow_surf, (255, 220, 80, 55), (glow_radius, glow_radius), int(glow_radius * 0.35))
        surface.blit(glow_surf, (640 - glow_radius, 320 - glow_radius))

        # Hearth Fire pit stones
        pygame.draw.ellipse(surface, (45, 35, 38), (540, 335, 200, 55))
        pygame.draw.ellipse(surface, (25, 18, 22), (555, 345, 170, 40))

        # Charcoal / Burning logs
        pygame.draw.line(surface, (70, 35, 25), (575, 360), (705, 345), 10)
        pygame.draw.line(surface, (60, 30, 20), (580, 345), (695, 360), 10)
        # Red hot embers on logs
        pygame.draw.circle(surface, (255, 70, 20), (635, 352), 6)
        pygame.draw.circle(surface, (255, 150, 40), (645, 350), 5)
        pygame.draw.circle(surface, (255, 120, 30), (620, 353), 4)

        # Dynamic Dancing Campfire Flames
        t = self.flame_timer
        f1_x = 640 + math.sin(t * 6.0) * 12
        f1_y = 210 + math.cos(t * 7.5) * 10
        f2_x = 625 + math.sin(t * 8.0 + 1.2) * 8
        f2_y = 240 + math.cos(t * 6.0) * 8
        f3_x = 655 + math.sin(t * 7.0 + 2.5) * 8
        f3_y = 235 + math.cos(t * 8.5) * 8

        # Outer crimson flame
        flame_outer = [
            (575, 350),
            (f2_x - 15, 280),
            (f1_x, f1_y),
            (f3_x + 15, 280),
            (705, 350),
            (670, 360),
            (640, 365),
            (610, 360)
        ]
        pygame.draw.polygon(surface, (220, 50, 25), flame_outer)

        # Inner vibrant orange flame
        flame_mid = [
            (595, 350),
            (f2_x, 290),
            (f1_x + 2, f1_y + 25),
            (f3_x, 290),
            (685, 350),
            (640, 360)
        ]
        pygame.draw.polygon(surface, (255, 140, 30), flame_mid)

        # Core bright yellow / white tongue
        flame_inner = [
            (615, 350),
            (640 + math.sin(t * 10) * 5, 265),
            (665, 350),
            (640, 355)
        ]
        pygame.draw.polygon(surface, (255, 235, 95), flame_inner)

        # Embers drifting upward
        for e in self.embers:
            alpha = max(0, min(255, int(255 * (e[4] / 1.4))))
            rad = max(1, int(e[5] * (e[4] / 1.4)))
            e_surf = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(e_surf, (*e[6], alpha), (rad + 1, rad + 1), rad)
            surface.blit(e_surf, (int(e[0] - rad), int(e[1] - rad)))

        # Status text
        msg_surf = FONTS['regular'].render(self.status_message, True, (215, 210, 230))
        surface.blit(msg_surf, msg_surf.get_rect(center=(640, 425)))

        if not self.action_taken:
            self.rest_btn.draw(surface)
            self.smith_btn.draw(surface)
        else:
            self.proceed_btn.draw(surface)
