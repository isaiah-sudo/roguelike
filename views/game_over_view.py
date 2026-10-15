"""
Game Over View: Victory and Defeat end-of-run screens.
"""
import pygame
from engine.ui import Button
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, COLOR_HEALTH_RED, FONTS
)

class GameOverView:
    def __init__(self, is_victory: bool, player, floor_reached: int):
        self.is_victory = is_victory
        self.player = player
        self.floor_reached = floor_reached
        self.restart_btn = Button((540, 560, 200, 52), "PLAY AGAIN", FONTS['medium'], bg_color=(120, 35, 45) if not is_victory else (45, 120, 70))

    def handle_event(self, event, mouse_pos) -> str:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.restart_btn.handle_event(event):
                return "restart"
        return "none"

    def update(self, dt, mouse_pos):
        self.restart_btn.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)

        if self.is_victory:
            header_color = COLOR_TEXT_GOLD
            header_text = "VICTORY ACHIEVED"
            sub_text = "You conquered the Crypt of the Necrolord and shattered the curse!"
        else:
            header_color = COLOR_HEALTH_RED
            header_text = "FALLEN IN BATTLE"
            sub_text = "Your bones now join the forgotten dead within the crypt..."

        # Header
        h_surf = FONTS['huge'].render(header_text, True, header_color)
        surface.blit(h_surf, h_surf.get_rect(center=(640, 160)))

        # Subtext
        s_surf = FONTS['regular'].render(sub_text, True, (200, 190, 215))
        surface.blit(s_surf, s_surf.get_rect(center=(640, 220)))

        # Run Statistics Panel
        panel = pygame.Rect(440, 270, 400, 240)
        pygame.draw.rect(surface, (25, 20, 32), panel, border_radius=10)
        pygame.draw.rect(surface, (85, 70, 105), panel, width=2, border_radius=10)

        stats = [
            f"Floor Reached: {self.floor_reached}",
            f"Cards in Deck: {len(self.player.deck)}",
            f"Relics Collected: {len(self.player.relics)}",
            f"Final Gold: {self.player.gold}"
        ]

        sy = 310
        for stat in stats:
            stat_surf = FONTS['medium'].render(stat, True, COLOR_TEXT_LIGHT)
            surface.blit(stat_surf, (panel.x + 35, sy))
            sy += 45

        self.restart_btn.draw(surface)
