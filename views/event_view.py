"""
Event View: Narrative mystery event choice screen.
"""
import pygame
from systems.events import GameEvent
from engine.ui import Button, draw_top_bar
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, FONTS
)

class EventView:
    def __init__(self, event: GameEvent, player):
        self.event = event
        self.player = player
        self.option_buttons: list[Button] = []
        self.continue_btn = Button((560, 580, 160, 48), "CONTINUE", FONTS['medium'])

        # Create option buttons
        btn_y = 380
        for text, _ in self.event.options:
            btn = Button((240, btn_y, 800, 45), text, FONTS['regular'], bg_color=(45, 38, 55), hover_color=(75, 60, 95))
            self.option_buttons.append(btn)
            btn_y += 60

    def handle_event(self, event, mouse_pos) -> str:
        if self.event.resolved:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.continue_btn.handle_event(event):
                    return "back_to_map"
            return "none"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, btn in enumerate(self.option_buttons):
                if btn.handle_event(event):
                    _, callback = self.event.options[idx]
                    self.event.result_text = callback(self.player)
                    self.event.resolved = True
                    break

        return "none"

    def update(self, dt, mouse_pos):
        if not self.event.resolved:
            for btn in self.option_buttons:
                btn.update(mouse_pos)
        else:
            self.continue_btn.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)
        draw_top_bar(surface, self.player, 0)

        # Event Card Panel
        panel_rect = pygame.Rect(180, 80, 920, 560)
        pygame.draw.rect(surface, (25, 20, 32), panel_rect, border_radius=14)
        pygame.draw.rect(surface, (85, 70, 105), panel_rect, width=2, border_radius=14)

        # Title
        title_surf = FONTS['title'].render(self.event.title, True, (245, 220, 150))
        surface.blit(title_surf, title_surf.get_rect(center=(640, 130)))

        # Story text word-wrapped
        story_words = self.event.story.split(' ')
        lines = []
        cur = []
        for w in story_words:
            test = ' '.join(cur + [w])
            if FONTS['regular'].size(test)[0] < 820:
                cur.append(w)
            else:
                lines.append(' '.join(cur))
                cur = [w]
        if cur:
            lines.append(' '.join(cur))

        story_y = 180
        for l in lines:
            line_surf = FONTS['regular'].render(l, True, (220, 215, 230))
            surface.blit(line_surf, line_surf.get_rect(center=(640, story_y)))
            story_y += 24

        # Choices or Outcome
        if not self.event.resolved:
            for btn in self.option_buttons:
                btn.draw(surface)
        else:
            res_box = pygame.Rect(240, 360, 800, 120)
            pygame.draw.rect(surface, (35, 30, 45), res_box, border_radius=8)
            pygame.draw.rect(surface, (120, 100, 150), res_box, width=1, border_radius=8)

            res_words = self.event.result_text.split(' ')
            rlines = []
            rcur = []
            for w in res_words:
                test = ' '.join(rcur + [w])
                if FONTS['regular'].size(test)[0] < 760:
                    rcur.append(w)
                else:
                    rlines.append(' '.join(rcur))
                    rcur = [w]
            if rcur:
                rlines.append(' '.join(rcur))

            ry = 390
            for rl in rlines:
                r_surf = FONTS['regular'].render(rl, True, COLOR_TEXT_GOLD)
                surface.blit(r_surf, r_surf.get_rect(center=(640, ry)))
                ry += 24

            self.continue_btn.draw(surface)
