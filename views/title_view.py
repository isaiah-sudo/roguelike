"""
Title View: Main Menu with Continue, New Run, Load Game, and Quit options.
Features dark fantasy gothic atmosphere with animated soul embers and ornate typography.
"""
import math
import random
import pygame
from engine.ui import Button
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED, FONTS
)
from systems.save_manager import has_any_save, get_latest_save_slot, get_slot_info


class TitleEmber:
    """Atmospheric soul ember rising from the crypt floor."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-15, 15)
        self.vy = random.uniform(-35, -80)
        self.radius = random.uniform(1.5, 3.5)
        self.lifetime = random.uniform(3.0, 6.0)
        self.max_lifetime = self.lifetime
        # Mystic purple, cyan, and fiery gold tints
        palette = [
            (210, 60, 80),    # Blood red
            (160, 70, 240),   # Void violet
            (60, 180, 240),   # Soul azure
            (255, 200, 70),   # Golden flame
        ]
        self.color = random.choice(palette)

    def update(self, dt):
        self.lifetime -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx += math.sin(self.lifetime * 4.0) * 8.0 * dt

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        alpha = int(220 * max(0.0, self.lifetime / self.max_lifetime))
        r = int(self.radius * (0.6 + 0.4 * (self.lifetime / self.max_lifetime)))
        if r <= 0:
            return
        glow_surf = pygame.Surface((r * 4 + 4, r * 4 + 4), pygame.SRCALPHA)
        center = (r * 2 + 2, r * 2 + 2)
        pygame.draw.circle(glow_surf, (*self.color, alpha // 3), center, r * 2)
        pygame.draw.circle(glow_surf, (*self.color, alpha), center, r)
        surface.blit(glow_surf, (int(self.x - center[0]), int(self.y - center[1])))


class TitleView:
    def __init__(self):
        self.anim_timer = 0.0
        self.embers = [TitleEmber(random.uniform(100, 1180), random.uniform(200, 720)) for _ in range(35)]

        self.refresh_save_status()

    def refresh_save_status(self):
        """Refreshes active save states when entering or returning to the title screen."""
        self.has_save = has_any_save()
        self.latest_slot = get_latest_save_slot()
        self.latest_info = get_slot_info(self.latest_slot) if self.latest_slot else None

        # Build Menu Buttons
        btn_w, btn_h = 280, 52
        center_x = 640 - btn_w // 2

        # 1. CONTINUE BUTTON
        self.continue_btn = Button(
            (center_x, 340, btn_w, btn_h),
            "CONTINUE RUN",
            FONTS['medium'],
            bg_color=(130, 35, 50) if self.has_save else (35, 28, 40),
            hover_color=(175, 45, 65) if self.has_save else (35, 28, 40),
            text_color=(255, 240, 220) if self.has_save else (90, 80, 100)
        )
        self.continue_btn.enabled = self.has_save

        # 2. NEW RUN BUTTON
        self.new_run_btn = Button(
            (center_x, 412, btn_w, btn_h),
            "NEW EXPEDITION",
            FONTS['medium'],
            bg_color=(45, 40, 65),
            hover_color=(75, 60, 105),
            text_color=COLOR_TEXT_LIGHT
        )

        # 3. LOAD GAME BUTTON
        self.load_game_btn = Button(
            (center_x, 484, btn_w, btn_h),
            "SAVED EXPEDITIONS",
            FONTS['medium'],
            bg_color=(40, 42, 60),
            hover_color=(60, 65, 95),
            text_color=COLOR_TEXT_LIGHT
        )

        # 4. QUIT BUTTON
        self.quit_btn = Button(
            (center_x, 556, btn_w, btn_h),
            "DEPART REALM",
            FONTS['medium'],
            bg_color=(32, 26, 38),
            hover_color=(55, 45, 65),
            text_color=(190, 180, 200)
        )

    def handle_event(self, event, mouse_pos) -> tuple[str, any]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.has_save and self.continue_btn.handle_event(event):
                play_sfx('card_draw', 0.6)
                return "continue", self.latest_slot

            if self.new_run_btn.handle_event(event):
                play_sfx('click', 0.6)
                return "new_run", None

            if self.load_game_btn.handle_event(event):
                play_sfx('click', 0.6)
                return "load_game", None

            if self.quit_btn.handle_event(event):
                play_sfx('click', 0.6)
                return "quit", None

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.has_save:
                    play_sfx('card_draw', 0.6)
                    return "continue", self.latest_slot
                else:
                    play_sfx('click', 0.6)
                    return "new_run", None
            elif event.key == pygame.K_n:
                play_sfx('click', 0.6)
                return "new_run", None
            elif event.key == pygame.K_l:
                play_sfx('click', 0.6)
                return "load_game", None
            elif event.key == pygame.K_ESCAPE:
                return "quit", None

        return "none", None

    def update(self, dt, mouse_pos):
        self.anim_timer += dt

        # Spawn & update soul embers
        if len(self.embers) < 40 and random.random() < 0.35:
            self.embers.append(TitleEmber(random.uniform(80, 1200), 730))

        for ember in self.embers:
            ember.update(dt)
        self.embers = [e for e in self.embers if e.lifetime > 0]

        # Update button hover states
        self.continue_btn.update(mouse_pos)
        self.new_run_btn.update(mouse_pos)
        self.load_game_btn.update(mouse_pos)
        self.quit_btn.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)

        # Atmospheric Background Vignette
        pulse = (math.sin(self.anim_timer * 1.5) + 1.0) * 0.5
        vignette_surf = pygame.Surface((1280, 720), pygame.SRCALPHA)
        # Deep crimson/purple radial glow from bottom center
        pygame.draw.circle(vignette_surf, (80, 20, 45, int(40 + pulse * 25)), (640, 500), 450)
        pygame.draw.circle(vignette_surf, (40, 15, 60, 60), (640, 360), 600)
        surface.blit(vignette_surf, (0, 0))

        # Draw soul embers behind UI
        for ember in self.embers:
            ember.draw(surface)

        # Ornate Central Frame Panel
        frame_rect = pygame.Rect(430, 70, 420, 570)
        pygame.draw.rect(surface, (22, 17, 30, 220), frame_rect, border_radius=16)
        pygame.draw.rect(surface, (80, 60, 105), frame_rect, width=2, border_radius=16)

        # Inner decorative gold border
        inner_rect = pygame.Rect(438, 78, 404, 554)
        pygame.draw.rect(surface, (120, 95, 55), inner_rect, width=1, border_radius=12)

        # Gothic Crest / Skull Emblem at Top of Frame
        crest_y = 118
        # Outer crest circle
        pygame.draw.circle(surface, (45, 30, 55), (640, crest_y), 32)
        pygame.draw.circle(surface, (180, 140, 70), (640, crest_y), 32, 2)
        # Inner glowing eye/diamond
        gem_color = (220, 50, 70) if not self.has_save else (255, 215, 80)
        gem_pts = [
            (640, crest_y - 18),
            (652, crest_y),
            (640, crest_y + 18),
            (628, crest_y)
        ]
        pygame.draw.polygon(surface, gem_color, gem_pts)
        pygame.draw.polygon(surface, (255, 255, 255), gem_pts, 1)

        # Title: CRYPT OF THE NECROLORD
        title_y = 185
        # Shadow
        shadow_surf = FONTS['huge'].render("CRYPT OF THE NECROLORD", True, (15, 8, 20))
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(642, title_y + 3)))
        # Main Title
        title_color = (255, 225, 120)
        title_surf = FONTS['huge'].render("CRYPT OF THE NECROLORD", True, title_color)
        surface.blit(title_surf, title_surf.get_rect(center=(640, title_y)))

        # Subtitle
        sub_y = 236
        sub_text = "DARK FANTASY DECKBUILDING ROGUELIKE"
        sub_surf = FONTS['small'].render(sub_text, True, (215, 195, 230))
        surface.blit(sub_surf, sub_surf.get_rect(center=(640, sub_y)))

        # Ornate divider line with diamond
        pygame.draw.line(surface, (120, 90, 60), (470, 265), (810, 265), 1)
        div_diamond = [(640, 261), (644, 265), (640, 269), (636, 265)]
        pygame.draw.polygon(surface, COLOR_TEXT_GOLD, div_diamond)

        # Run summary tooltip/label for Continue button
        if self.has_save and self.latest_info:
            char_title = self.latest_info.get("char_name", "Hero")
            act_num = self.latest_info.get("act", 1)
            fl_num = self.latest_info.get("current_floor", 1)
            hp_curr = self.latest_info.get("hp", 0)
            hp_max = self.latest_info.get("max_hp", 0)
            gold = self.latest_info.get("gold", 0)
            slot_id = self.latest_info.get("slot_id", 1)
            summary_txt = f"Slot {slot_id}: {char_title} • Act {act_num}-F{fl_num} • {hp_curr}/{hp_max} HP • {gold}g"
            sum_surf = FONTS['small'].render(summary_txt, True, (240, 210, 140))
            surface.blit(sum_surf, sum_surf.get_rect(center=(640, 316)))
        else:
            prompt_surf = FONTS['small'].render("No ongoing expedition found", True, (120, 110, 130))
            surface.blit(prompt_surf, prompt_surf.get_rect(center=(640, 316)))

        # Draw Menu Buttons
        self.continue_btn.draw(surface)
        self.new_run_btn.draw(surface)
        self.load_game_btn.draw(surface)
        self.quit_btn.draw(surface)

        # Footer hints and version
        ver_surf = FONTS['small'].render("Crypt Engine v1.2.0 • Deckbuilder Edition", True, (90, 80, 105))
        surface.blit(ver_surf, (25, 692))

        ctrl_surf = FONTS['small'].render("[Enter] Embark   [N] New Run   [L] Saved Games   [Esc] Depart", True, (110, 100, 125))
        surface.blit(ctrl_surf, ctrl_surf.get_rect(bottomright=(1255, 712)))
