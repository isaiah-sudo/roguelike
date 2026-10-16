"""
Title View: Main Menu with Continue, New Run, Load Game, Quit options,
and integrated GitHub Auto-Update System with in-game patch notes.
Features dark fantasy gothic atmosphere with animated soul embers and ornate typography.
"""
import math
import random
import pygame
from engine.ui import Button
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, COLOR_TEXT_MUTED,
    COLOR_CARD_BORDER, FONTS, GAME_VERSION
)
from systems.save_manager import has_any_save, get_latest_save_slot, get_slot_info
from systems.updater import UpdateManager, UpdateState


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


def format_release_notes(raw_body: str, max_width_px: int, font) -> list[tuple[str, tuple[int, int, int]]]:
    """Formats markdown release notes into clean display lines."""
    lines = []
    for raw_line in raw_body.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append(("", (200, 200, 200)))
            continue
        color = (220, 215, 230)
        if line.startswith("#"):
            line = line.lstrip("#").strip()
            color = (255, 220, 110)
        elif line.startswith("-") or line.startswith("*"):
            color = (195, 185, 215)
        
        words = line.split(" ")
        curr = ""
        for w in words:
            clean_w = w.replace("**", "").replace("`", "")
            test = f"{curr} {clean_w}".strip()
            if font.size(test)[0] <= max_width_px:
                curr = test
            else:
                if curr:
                    lines.append((curr, color))
                curr = clean_w
        if curr:
            lines.append((curr, color))
    return lines


class TitleView:
    def __init__(self):
        self.anim_timer = 0.0
        self.embers = [TitleEmber(random.uniform(100, 1180), random.uniform(200, 720)) for _ in range(35)]

        self.refresh_save_status()

        # Initialize Auto-Updater
        self.updater = UpdateManager(current_version=GAME_VERSION)
        self.updater.check_for_updates(async_check=True)

        # Update Card UI Buttons
        self.apply_btn = Button(
            (890, 290, 225, 48),
            "DOWNLOAD & APPLY",
            FONTS['bold'],
            bg_color=(150, 35, 50),
            hover_color=(195, 45, 65),
            text_color=(255, 245, 220)
        )
        self.notes_btn = Button(
            (1125, 290, 110, 48),
            "NOTES",
            FONTS['bold'],
            bg_color=(45, 40, 65),
            hover_color=(75, 60, 105),
            text_color=COLOR_TEXT_LIGHT
        )
        self.restart_btn = Button(
            (890, 280, 345, 52),
            "RESTART & APPLY UPDATE",
            FONTS['bold'],
            bg_color=(40, 135, 75),
            hover_color=(55, 175, 100),
            text_color=(255, 255, 255)
        )
        self.check_btn = Button(
            (320, 686, 64, 22),
            "Check",
            FONTS.get('tiny', FONTS['small']),
            bg_color=(36, 30, 46),
            hover_color=(58, 48, 74),
            text_color=(190, 180, 210)
        )

        # Release Notes Modal
        self.showing_notes = False
        self.notes_scroll_y = 0
        self.max_scroll_y = 0
        self.cached_notes = None
        self.last_notes_body = None
        self.modal_close_btn = Button(
            (500, 580, 130, 42),
            "CLOSE",
            FONTS['bold'],
            bg_color=(45, 40, 55),
            hover_color=(70, 60, 85)
        )
        self.modal_apply_btn = Button(
            (650, 580, 210, 42),
            "DOWNLOAD & APPLY",
            FONTS['bold'],
            bg_color=(150, 35, 50),
            hover_color=(195, 45, 65),
            text_color=(255, 245, 220)
        )

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
        # Handle Release Notes Modal if open
        if self.showing_notes:
            if event.type == pygame.MOUSEWHEEL:
                self.notes_scroll_y -= event.y * 35
                self.notes_scroll_y = max(0, min(self.max_scroll_y, self.notes_scroll_y))
                return "none", None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.modal_close_btn.handle_event(event):
                    play_sfx('click', 0.5)
                    self.showing_notes = False
                    return "none", None

                if self.modal_apply_btn.handle_event(event):
                    play_sfx('click', 0.6)
                    state = self.updater.state
                    if state == UpdateState.UPDATE_AVAILABLE:
                        self.updater.start_download(async_download=True)
                        self.showing_notes = False
                    elif state == UpdateState.DOWNLOADED:
                        if self.updater.apply_update():
                            return "quit_for_update", None
                    return "none", None

            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.showing_notes = False
                return "none", None

            # Block background clicks when modal is open
            return "none", None

        # Main Screen Interactions
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check button in footer
            if self.updater.state in (UpdateState.UP_TO_DATE, UpdateState.ERROR) and self.check_btn.handle_event(event):
                play_sfx('click', 0.5)
                self.updater.check_for_updates(async_check=True)
                return "none", None

            # Update Card buttons
            state = self.updater.state
            if state == UpdateState.UPDATE_AVAILABLE:
                if self.apply_btn.handle_event(event):
                    play_sfx('click', 0.6)
                    self.updater.start_download(async_download=True)
                    return "none", None
                if self.notes_btn.handle_event(event):
                    play_sfx('click', 0.5)
                    self.showing_notes = True
                    self.notes_scroll_y = 0
                    return "none", None

            elif state == UpdateState.DOWNLOADED:
                if self.restart_btn.handle_event(event):
                    play_sfx('click', 0.7)
                    if self.updater.apply_update():
                        return "quit_for_update", None
                    return "none", None
                if self.notes_btn.handle_event(event):
                    play_sfx('click', 0.5)
                    self.showing_notes = True
                    self.notes_scroll_y = 0
                    return "none", None

            # Standard Title Menu
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

        if self.showing_notes:
            self.modal_close_btn.update(mouse_pos)
            self.modal_apply_btn.update(mouse_pos)
            return

        # Update button hover states
        self.continue_btn.update(mouse_pos)
        self.new_run_btn.update(mouse_pos)
        self.load_game_btn.update(mouse_pos)
        self.quit_btn.update(mouse_pos)

        # Update updater buttons
        if self.updater.state in (UpdateState.UP_TO_DATE, UpdateState.ERROR):
            self.check_btn.update(mouse_pos)
        elif self.updater.state == UpdateState.UPDATE_AVAILABLE:
            self.apply_btn.update(mouse_pos)
            self.notes_btn.update(mouse_pos)
        elif self.updater.state == UpdateState.DOWNLOADED:
            self.restart_btn.update(mouse_pos)
            self.notes_btn.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)

        # Atmospheric Background Vignette
        pulse = (math.sin(self.anim_timer * 1.5) + 1.0) * 0.5
        vignette_surf = pygame.Surface((1280, 720), pygame.SRCALPHA)
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
        pygame.draw.circle(surface, (45, 30, 55), (640, crest_y), 32)
        pygame.draw.circle(surface, (180, 140, 70), (640, crest_y), 32, 2)
        gem_color = (220, 50, 70) if not self.has_save else (255, 215, 80)
        gem_pts = [
            (640, crest_y - 18),
            (652, crest_y),
            (640, crest_y + 18),
            (628, crest_y)
        ]
        pygame.draw.polygon(surface, gem_color, gem_pts)
        pygame.draw.polygon(surface, (255, 255, 255), gem_pts, 1)

        # Main Title
        title_y = 185
        shadow_surf = FONTS['huge'].render("CRYPT OF THE NECROLORD", True, (15, 8, 20))
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(642, title_y + 3)))
        title_surf = FONTS['huge'].render("CRYPT OF THE NECROLORD", True, (255, 225, 120))
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

        # Draw Auto-Update Card (on the right side)
        self._draw_update_card(surface)

        # Footer hints & Auto-Update status
        self._draw_footer(surface)

        # Draw Release Notes Modal (if open)
        if self.showing_notes:
            self._draw_release_notes_modal(surface)

    def _draw_update_card(self, surface):
        """Draws the prominent gothic update card on the right side of the screen."""
        state = self.updater.state
        if state not in (UpdateState.UPDATE_AVAILABLE, UpdateState.DOWNLOADING, UpdateState.DOWNLOADED):
            return

        info = self.updater.update_info
        if not info:
            return

        card_rect = pygame.Rect(870, 130, 385, 230)
        # Background panel
        pygame.draw.rect(surface, (24, 18, 32, 235), card_rect, border_radius=12)
        
        # Pulsing ornate border
        pulse = (math.sin(self.anim_timer * 3.5) + 1.0) * 0.5
        border_col = (
            int(180 + pulse * 60),
            int(130 + pulse * 60),
            int(60 + pulse * 40)
        ) if state != UpdateState.DOWNLOADED else (
            int(70 + pulse * 40),
            int(180 + pulse * 65),
            int(110 + pulse * 40)
        )
        pygame.draw.rect(surface, border_col, card_rect, width=2, border_radius=12)

        # Inner subtle gold border
        inner_box = pygame.Rect(876, 136, 373, 218)
        pygame.draw.rect(surface, (85, 65, 45), inner_box, width=1, border_radius=8)

        # Header badge icon & title
        badge_rect = pygame.Rect(888, 148, 130, 22)
        badge_bg = (130, 35, 45) if state != UpdateState.DOWNLOADED else (35, 110, 65)
        pygame.draw.rect(surface, badge_bg, badge_rect, border_radius=4)
        badge_lbl = "NEW VERSION" if state != UpdateState.DOWNLOADED else "DOWNLOAD READY"
        b_txt = FONTS.get('tiny', FONTS['small']).render(badge_lbl, True, (255, 245, 230))
        surface.blit(b_txt, b_txt.get_rect(center=badge_rect.center))

        # Version title
        v_surf = FONTS['medium'].render(f"Update {info.tag_name}", True, (255, 225, 120))
        surface.blit(v_surf, (888, 178))

        # Size & installer label
        mb_size = f"{info.asset_size / (1024*1024):.1f} MB" if info.asset_size > 0 else "Installer"
        asset_txt = f"{info.asset_name} ({mb_size})" if info.asset_name else f"GitHub Release ({mb_size})"
        if len(asset_txt) > 38:
            asset_txt = asset_txt[:35] + "..."
        a_surf = FONTS['small'].render(asset_txt, True, (200, 190, 220))
        surface.blit(a_surf, (888, 208))

        # Divider
        pygame.draw.line(surface, (70, 55, 80), (888, 234), (1237, 234), 1)

        if state == UpdateState.UPDATE_AVAILABLE:
            note_preview = info.title if info.title else "Bug fixes & balance adjustments"
            if len(note_preview) > 36:
                note_preview = note_preview[:33] + "..."
            p_surf = FONTS['small'].render(note_preview, True, (170, 160, 190))
            surface.blit(p_surf, (888, 245))

            self.apply_btn.draw(surface)
            self.notes_btn.draw(surface)

        elif state == UpdateState.DOWNLOADING:
            pct = int(self.updater.progress * 100)
            mb_down = self.updater.bytes_downloaded / (1024 * 1024)
            mb_tot = max(0.1, self.updater.total_bytes / (1024 * 1024))
            
            prog_str = f"Downloading: {pct}% ({mb_down:.1f} MB / {mb_tot:.1f} MB)"
            pr_surf = FONTS['bold'].render(prog_str, True, (255, 215, 100))
            surface.blit(pr_surf, (888, 248))

            # Progress Bar Track
            bar_rect = pygame.Rect(888, 276, 345, 22)
            pygame.draw.rect(surface, (32, 22, 36), bar_rect, border_radius=6)
            fill_w = max(4, int(345 * self.updater.progress))
            fill_rect = pygame.Rect(888, 276, fill_w, 22)
            pygame.draw.rect(surface, (195, 45, 65), fill_rect, border_radius=6)
            # Gold tip highlight
            if fill_w > 8:
                tip_rect = pygame.Rect(888 + fill_w - 6, 276, 6, 22)
                pygame.draw.rect(surface, (255, 220, 110), tip_rect, border_radius=3)
            pygame.draw.rect(surface, (130, 95, 65), bar_rect, width=1, border_radius=6)

            sub_surf = FONTS.get('tiny', FONTS['small']).render("Streaming update package in background...", True, (160, 150, 175))
            surface.blit(sub_surf, (888, 308))

        elif state == UpdateState.DOWNLOADED:
            self.restart_btn.draw(surface)
            hint_surf = FONTS.get('tiny', FONTS['small']).render("Click to close game and launch seamless installer", True, (160, 220, 175))
            surface.blit(hint_surf, hint_surf.get_rect(center=(card_rect.centerx, 344)))

    def _draw_footer(self, surface):
        """Draws the bottom status bar, including version and auto-update indicator."""
        state = self.updater.state

        if state == UpdateState.CHECKING:
            dot_pulse = (math.sin(self.anim_timer * 4.0) + 1.0) * 0.5
            dot_alpha = int(120 + dot_pulse * 135)
            ver_txt = f"Crypt Engine v{GAME_VERSION} • Checking for updates..."
            ver_surf = FONTS['small'].render(ver_txt, True, (160, 150, 190))
            surface.blit(ver_surf, (25, 690))
            # Glowing dot
            glow_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (220, 180, 80, dot_alpha), (6, 6), 5)
            surface.blit(glow_surf, (ver_surf.get_width() + 32, 693))

        elif state == UpdateState.UP_TO_DATE:
            ver_txt = f"Crypt Engine v{GAME_VERSION} • Up to date ✓"
            ver_surf = FONTS['small'].render(ver_txt, True, (100, 175, 120))
            surface.blit(ver_surf, (25, 690))
            self.check_btn.rect.x = ver_surf.get_width() + 35
            self.check_btn.text = "Check"
            self.check_btn.draw(surface)

        elif state == UpdateState.ERROR:
            err_short = self.updater.error_message or "Offline"
            ver_txt = f"Crypt Engine v{GAME_VERSION} • Update check: {err_short}"
            ver_surf = FONTS['small'].render(ver_txt, True, (180, 110, 120))
            surface.blit(ver_surf, (25, 690))
            self.check_btn.rect.x = ver_surf.get_width() + 35
            self.check_btn.text = "Retry"
            self.check_btn.draw(surface)

        elif state in (UpdateState.UPDATE_AVAILABLE, UpdateState.DOWNLOADING, UpdateState.DOWNLOADED):
            info = self.updater.update_info
            v_tag = info.tag_name if info else "New"
            ver_txt = f"Crypt Engine v{GAME_VERSION} • ⚡ Update {v_tag} Available"
            ver_surf = FONTS['small'].render(ver_txt, True, COLOR_TEXT_GOLD)
            surface.blit(ver_surf, (25, 690))

        ctrl_surf = FONTS['small'].render("[Enter] Embark   [N] New Run   [L] Saved Games   [Esc] Depart", True, (110, 100, 125))
        surface.blit(ctrl_surf, ctrl_surf.get_rect(bottomright=(1255, 712)))

    def _draw_release_notes_modal(self, surface):
        """Renders an ornate parchment popup modal displaying GitHub release notes."""
        info = self.updater.update_info
        if not info:
            return

        # Dark overlay
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((10, 8, 14, 215))
        surface.blit(overlay, (0, 0))

        # Modal Window
        modal_rect = pygame.Rect(260, 50, 760, 620)
        pygame.draw.rect(surface, (25, 20, 32), modal_rect, border_radius=14)
        pygame.draw.rect(surface, (180, 140, 75), modal_rect, width=2, border_radius=14)

        # Inner border
        inner_m = pygame.Rect(268, 58, 744, 604)
        pygame.draw.rect(surface, (70, 50, 85), inner_m, width=1, border_radius=10)

        # Header Title
        title_surf = FONTS['title'].render("RELEASE NOTES", True, (255, 225, 120))
        surface.blit(title_surf, title_surf.get_rect(center=(640, 95)))

        sub_txt = f"{info.title} ({info.tag_name})"
        sub_surf = FONTS['regular'].render(sub_txt, True, (215, 205, 230))
        surface.blit(sub_surf, sub_surf.get_rect(center=(640, 128)))

        pygame.draw.line(surface, (120, 95, 60), (290, 148), (990, 148), 1)

        # Parse & word-wrap notes body
        if self.cached_notes is None or self.last_notes_body != info.body:
            self.cached_notes = format_release_notes(info.body, 680, FONTS['small'])
            self.last_notes_body = info.body

        # Scrollable Viewport
        view_rect = pygame.Rect(290, 160, 700, 395)
        clip_surf = pygame.Surface((view_rect.width, view_rect.height), pygame.SRCALPHA)

        line_h = 22
        total_content_h = len(self.cached_notes) * line_h
        self.max_scroll_y = max(0, total_content_h - view_rect.height)

        cur_y = -self.notes_scroll_y
        for text, color in self.cached_notes:
            if -line_h <= cur_y <= view_rect.height:
                t_surf = FONTS['small'].render(text, True, color)
                clip_surf.blit(t_surf, (0, cur_y))
            cur_y += line_h

        surface.blit(clip_surf, view_rect)

        # Scrollbar Track & Thumb
        if self.max_scroll_y > 0:
            track_rect = pygame.Rect(998, 160, 6, 395)
            pygame.draw.rect(surface, (45, 35, 55), track_rect, border_radius=3)
            thumb_h = max(30, int(395 * (view_rect.height / total_content_h)))
            thumb_y = 160 + int((395 - thumb_h) * (self.notes_scroll_y / self.max_scroll_y))
            thumb_rect = pygame.Rect(998, thumb_y, 6, thumb_h)
            pygame.draw.rect(surface, (200, 165, 80), thumb_rect, border_radius=3)

        # Bottom Action Bar
        pygame.draw.line(surface, (80, 65, 95), (290, 565), (990, 565), 1)
        self.modal_close_btn.draw(surface)

        # Update modal action button according to updater state
        if self.updater.state == UpdateState.DOWNLOADED:
            self.modal_apply_btn.text = "RESTART & APPLY"
            self.modal_apply_btn.bg_color = (40, 135, 75)
            self.modal_apply_btn.hover_color = (55, 175, 100)
        else:
            self.modal_apply_btn.text = "DOWNLOAD & APPLY"
            self.modal_apply_btn.bg_color = (150, 35, 50)
            self.modal_apply_btn.hover_color = (195, 45, 65)
        self.modal_apply_btn.draw(surface)
