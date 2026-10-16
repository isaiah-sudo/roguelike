"""
Reward View: Loot drafting screen after combat victory.
"""
import pygame
from systems.reward import CombatReward
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.ui import Button, draw_top_bar, draw_tooltip
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, FONTS
)

class RewardView:
    def __init__(self, reward: CombatReward, player):
        self.reward = reward
        self.player = player
        self.proceed_btn = Button(
            (520, 620, 240, 48),
            "ASCEND TO NEXT ACT" if reward.is_boss else "PROCEED",
            FONTS['medium'],
            bg_color=(160, 45, 60) if reward.is_boss else (45, 110, 65),
            hover_color=(200, 60, 80) if reward.is_boss else (65, 140, 85)
        )
        self.skip_card_btn = Button((565, 550, 150, 36), "Skip Card", FONTS['regular'], bg_color=(60, 45, 65))
        
        self.drafting_cards = False
        self.drafting_boss_relics = False
        self.hovered_card_idx = -1
        self.hovered_boss_relic_idx = -1

    def handle_event(self, event, mouse_pos) -> str:
        if self.drafting_cards:
            # Check card clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.skip_card_btn.handle_event(event):
                    self.drafting_cards = False
                    self.reward.card_claimed = True
                    return "none"

                card_rects = self._get_draft_card_rects()
                for idx, (rect, card) in enumerate(card_rects):
                    if rect.collidepoint(event.pos):
                        self.reward.choose_card(self.player, card)
                        self.drafting_cards = False
                        return "none"
            return "none"

        if self.drafting_boss_relics:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                relic_rects = self._get_boss_relic_rects()
                for idx, (rect, relic) in enumerate(relic_rects):
                    if rect.collidepoint(event.pos):
                        self.reward.choose_boss_relic(self.player, relic)
                        self.drafting_boss_relics = False
                        return "none"
            return "none"

        # Claiming main loot items
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.proceed_btn.handle_event(event):
                # Automatically claim gold if not claimed
                if not self.reward.gold_claimed:
                    self.reward.claim_gold(self.player)
                return "ascend_act" if self.reward.is_boss else "back_to_map"

            # Gold button
            if not self.reward.gold_claimed:
                gold_rect = pygame.Rect(440, 180, 400, 48)
                if gold_rect.collidepoint(event.pos):
                    self.reward.claim_gold(self.player)
                    return "none"

            # Card button
            if not self.reward.card_claimed:
                card_rect = pygame.Rect(440, 240, 400, 48)
                if card_rect.collidepoint(event.pos):
                    self.drafting_cards = True
                    play_sfx('card_draw', 0.5)
                    return "none"

            # Boss Relic Draft button (if boss fight)
            if self.reward.is_boss and not self.reward.boss_relic_claimed:
                boss_r_rect = pygame.Rect(440, 300, 400, 48)
                if boss_r_rect.collidepoint(event.pos):
                    self.drafting_boss_relics = True
                    play_sfx('buff', 0.6)
                    return "none"

            # Regular Relic button
            if self.reward.relic_reward and not self.reward.relic_claimed:
                relic_rect = pygame.Rect(440, 360, 400, 48)
                if relic_rect.collidepoint(event.pos):
                    self.reward.claim_relic(self.player)
                    return "none"

            # Potion button
            if self.reward.potion_reward and not self.reward.potion_claimed:
                pot_rect = pygame.Rect(440, 420, 400, 48)
                if pot_rect.collidepoint(event.pos):
                    self.reward.claim_potion(self.player)
                    return "none"

        return "none"

    def _get_draft_card_rects(self):
        cards = self.reward.card_options
        spacing = 240
        start_x = 640 - (spacing * (len(cards) - 1) + CARD_WIDTH) / 2
        y = 260

        rects = []
        for i, card in enumerate(cards):
            x = start_x + i * spacing
            rect = pygame.Rect(x, y - (20 if i == self.hovered_card_idx else 0), CARD_WIDTH, CARD_HEIGHT)
            rects.append((rect, card))
        return rects

    def _get_boss_relic_rects(self):
        relics = self.reward.boss_relic_options
        card_w = 320
        card_h = 240
        spacing = 360
        start_x = 640 - (spacing * (len(relics) - 1) + card_w) / 2
        y = 260

        rects = []
        for i, relic in enumerate(relics):
            x = start_x + i * spacing
            rect = pygame.Rect(x, y - (15 if i == self.hovered_boss_relic_idx else 0), card_w, card_h)
            rects.append((rect, relic))
        return rects

    def update(self, dt, mouse_pos):
        self.proceed_btn.update(mouse_pos)
        self.skip_card_btn.update(mouse_pos)

        if self.drafting_cards:
            self.hovered_card_idx = -1
            for idx, (rect, _) in enumerate(self._get_draft_card_rects()):
                if rect.collidepoint(mouse_pos):
                    self.hovered_card_idx = idx
                    break

        if self.drafting_boss_relics:
            self.hovered_boss_relic_idx = -1
            for idx, (rect, _) in enumerate(self._get_boss_relic_rects()):
                if rect.collidepoint(mouse_pos):
                    self.hovered_boss_relic_idx = idx
                    break

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        surface.fill(COLOR_BG_DARK)
        draw_top_bar(surface, self.player, 0, mouse_pos=mouse_pos)

        if self.drafting_cards:
            title = FONTS['title'].render("CHOOSE A CARD", True, (240, 220, 160))
            surface.blit(title, title.get_rect(center=(640, 160)))

            for idx, (rect, card) in enumerate(self._get_draft_card_rects()):
                draw_card(surface, card, rect.x, rect.y, is_hovered=(idx == self.hovered_card_idx), is_playable=True)

            self.skip_card_btn.draw(surface)
            return

        if self.drafting_boss_relics:
            title = FONTS['title'].render("CLAIM A BOSS RELIC", True, COLOR_TEXT_GOLD)
            surface.blit(title, title.get_rect(center=(640, 150)))
            sub = FONTS['regular'].render("Choose 1 powerful relic to aid your ascent into deeper perils", True, (200, 190, 215))
            surface.blit(sub, sub.get_rect(center=(640, 190)))

            for idx, (rect, relic) in enumerate(self._get_boss_relic_rects()):
                is_hover = (idx == self.hovered_boss_relic_idx)
                bg_col = (45, 32, 55) if is_hover else (30, 22, 38)
                pygame.draw.rect(surface, bg_col, rect, border_radius=12)
                pygame.draw.rect(surface, (255, 215, 80) if is_hover else (130, 95, 160), rect, width=2 if not is_hover else 3, border_radius=12)

                # Name
                r_name = FONTS['medium'].render(relic.name, True, COLOR_TEXT_GOLD)
                surface.blit(r_name, r_name.get_rect(center=(rect.centerx, rect.y + 35)))

                # Type badge
                badge = FONTS['small'].render("[BOSS RELIC]", True, (255, 120, 100))
                surface.blit(badge, badge.get_rect(center=(rect.centerx, rect.y + 65)))

                # Description text
                words = relic.description.split()
                lines = []
                curr_line = []
                for word in words:
                    curr_line.append(word)
                    if len(" ".join(curr_line)) > 30:
                        lines.append(" ".join(curr_line))
                        curr_line = []
                if curr_line:
                    lines.append(" ".join(curr_line))

                ly = rect.y + 105
                for line in lines:
                    rendered_line = FONTS['small'].render(line, True, (230, 225, 240))
                    surface.blit(rendered_line, rendered_line.get_rect(center=(rect.centerx, ly)))
                    ly += 22

                # Pick banner
                pick_txt = FONTS['bold'].render("CLICK TO CLAIM" if is_hover else "CHOOSE", True, (255, 255, 255) if is_hover else (160, 150, 180))
                surface.blit(pick_txt, pick_txt.get_rect(center=(rect.centerx, rect.bottom - 28)))
            return

        # Main reward menu
        header_text = "BOSS SLAIN - SPOILS OF WAR!" if self.reward.is_boss else "VICTORY!"
        header_color = (255, 215, 60) if self.reward.is_boss else COLOR_TEXT_GOLD
        header = FONTS['huge'].render(header_text, True, header_color)
        surface.blit(header, header.get_rect(center=(640, 115)))

        # 1. Gold reward
        gold_rect = pygame.Rect(440, 180, 400, 48)
        gold_bg = (40, 32, 50) if not self.reward.gold_claimed else (25, 20, 30)
        pygame.draw.rect(surface, gold_bg, gold_rect, border_radius=8)
        pygame.draw.rect(surface, (140, 120, 70), gold_rect, width=1, border_radius=8)
        gold_str = f"+ {self.reward.gold} Gold" if not self.reward.gold_claimed else "Claimed Gold"
        txt_col = COLOR_TEXT_GOLD if not self.reward.gold_claimed else (120, 110, 90)
        txt = FONTS['medium'].render(gold_str, True, txt_col)
        surface.blit(txt, txt.get_rect(center=gold_rect.center))

        # 2. Add Card to Deck
        card_rect = pygame.Rect(440, 240, 400, 48)
        card_bg = (40, 32, 50) if not self.reward.card_claimed else (25, 20, 30)
        pygame.draw.rect(surface, card_bg, card_rect, border_radius=8)
        pygame.draw.rect(surface, (100, 140, 200), card_rect, width=1, border_radius=8)
        card_str = ("Choose Rare Upgraded Card" if self.reward.is_boss else "Choose a Card to add to your Deck") if not self.reward.card_claimed else "Card Drafted"
        txt_col = (255, 230, 120) if self.reward.is_boss and not self.reward.card_claimed else (COLOR_TEXT_LIGHT if not self.reward.card_claimed else (100, 95, 110))
        txt = FONTS['medium'].render(card_str, True, txt_col)
        surface.blit(txt, txt.get_rect(center=card_rect.center))

        # 3. Boss Relic Choice Button
        if self.reward.is_boss:
            boss_r_rect = pygame.Rect(440, 300, 400, 48)
            boss_bg = (55, 30, 65) if not self.reward.boss_relic_claimed else (25, 20, 30)
            pygame.draw.rect(surface, boss_bg, boss_r_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 215, 80), boss_r_rect, width=2 if not self.reward.boss_relic_claimed else 1, border_radius=8)
            b_str = "👑 Choose 1 of 3 Boss Relics" if not self.reward.boss_relic_claimed else "Boss Relic Chosen"
            b_col = COLOR_TEXT_GOLD if not self.reward.boss_relic_claimed else (100, 95, 110)
            txt = FONTS['medium'].render(b_str, True, b_col)
            surface.blit(txt, txt.get_rect(center=boss_r_rect.center))

        hover_tooltip = None

        # 4. Relic reward if present
        if self.reward.relic_reward:
            relic_rect = pygame.Rect(440, 360, 400, 48)
            is_hov = relic_rect.collidepoint(mouse_pos) if not self.reward.relic_claimed else False
            relic_bg = (55, 42, 68) if is_hov else ((40, 32, 50) if not self.reward.relic_claimed else (25, 20, 30))
            pygame.draw.rect(surface, relic_bg, relic_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 215, 80) if is_hov else (200, 160, 80), relic_rect, width=2 if is_hov else 1, border_radius=8)
            relic_str = f"Relic: {self.reward.relic_reward.name} ({self.reward.relic_reward.description})" if not self.reward.relic_claimed else "Relic Claimed"
            txt_col = (255, 230, 140) if not self.reward.relic_claimed else (100, 95, 110)
            txt = FONTS['small'].render(relic_str, True, txt_col)
            surface.blit(txt, txt.get_rect(center=relic_rect.center))
            if is_hov:
                hover_tooltip = (mouse_pos[0], mouse_pos[1] + 15, self.reward.relic_reward.name, self.reward.relic_reward.description, "REWARD RELIC", (255, 215, 0))

        # 5. Potion reward if present
        if self.reward.potion_reward:
            pot_rect = pygame.Rect(440, 420, 400, 48)
            is_hov = pot_rect.collidepoint(mouse_pos) if not self.reward.potion_claimed else False
            pot_bg = (45, 55, 75) if is_hov else ((40, 32, 50) if not self.reward.potion_claimed else (25, 20, 30))
            pygame.draw.rect(surface, pot_bg, pot_rect, border_radius=8)
            pygame.draw.rect(surface, (160, 230, 255) if is_hov else (120, 200, 140), pot_rect, width=2 if is_hov else 1, border_radius=8)
            pot_str = f"Potion: {self.reward.potion_reward.name}" if not self.reward.potion_claimed else "Potion Claimed"
            txt_col = (140, 240, 160) if not self.reward.potion_claimed else (100, 95, 110)
            txt = FONTS['medium'].render(pot_str, True, txt_col)
            surface.blit(txt, txt.get_rect(center=pot_rect.center))
            if is_hov:
                hover_tooltip = (mouse_pos[0], mouse_pos[1] + 15, self.reward.potion_reward.name, self.reward.potion_reward.description, "REWARD POTION", (140, 200, 255))

        if hover_tooltip:
            draw_tooltip(surface, hover_tooltip[0], hover_tooltip[1], hover_tooltip[2], hover_tooltip[3], hover_tooltip[4], hover_tooltip[5])

        self.proceed_btn.draw(surface)

