"""
Load Game View: Expedition save slot browser.
Allows players to inspect, resume, or purge saved runs across slots, or embark on a new run.
"""
import pygame
from engine.ui import Button, HealthBar
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, COLOR_HEALTH_RED, FONTS
)
from systems.save_manager import (
    NUM_SLOTS, list_all_slots, get_slot_info, delete_save
)

CHAR_COLORS = {
    "blood_knight": (210, 45, 60),
    "shadow_assassin": (45, 185, 110),
    "void_necromancer": (160, 70, 230),
    "tempest_herald": (60, 170, 255),
    "radiant_templar": (245, 200, 60),
}


class LoadGameView:
    def __init__(self):
        self.confirm_delete_slot = None  # Holds slot_id awaiting delete confirmation
        self.back_btn = Button((520, 642, 240, 48), "BACK TO MENU", FONTS['medium'],
                               bg_color=(38, 32, 48), hover_color=(60, 50, 75))
        self.refresh_slots()

    def refresh_slots(self):
        self.slots = list_all_slots()
        self.slot_buttons = {}

        card_w = 370
        card_h = 475
        start_x = 55
        spacing = 400
        card_y = 135

        for slot_info in self.slots:
            sid = slot_info["slot_id"]
            rx = start_x + (sid - 1) * spacing
            rect = pygame.Rect(rx, card_y, card_w, card_h)

            if slot_info.get("exists"):
                load_btn = Button(
                    (rx + 25, card_y + 360, card_w - 50, 44),
                    "RESUME RUN",
                    FONTS['medium'],
                    bg_color=(125, 35, 48),
                    hover_color=(165, 45, 62)
                )
                del_btn = Button(
                    (rx + 25, card_y + 414, card_w - 50, 36),
                    "PURGE RUN" if self.confirm_delete_slot != sid else "CONFIRM PURGE?",
                    FONTS['small'],
                    bg_color=(50, 25, 30) if self.confirm_delete_slot != sid else (180, 30, 40),
                    hover_color=(80, 35, 45) if self.confirm_delete_slot != sid else (210, 40, 50),
                    text_color=(220, 170, 180) if self.confirm_delete_slot != sid else (255, 255, 255)
                )
                self.slot_buttons[sid] = {
                    "rect": rect,
                    "load": load_btn,
                    "delete": del_btn,
                    "new": None
                }
            else:
                new_btn = Button(
                    (rx + 35, card_y + 380, card_w - 70, 48),
                    "START RUN",
                    FONTS['medium'],
                    bg_color=(45, 40, 60),
                    hover_color=(75, 62, 100)
                )
                self.slot_buttons[sid] = {
                    "rect": rect,
                    "load": None,
                    "delete": None,
                    "new": new_btn
                }

    def handle_event(self, event, mouse_pos) -> tuple[str, any]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.handle_event(event):
                play_sfx('click', 0.5)
                return "back_to_title", None

            for sid, btns in self.slot_buttons.items():
                if btns["load"] and btns["load"].handle_event(event):
                    play_sfx('card_draw', 0.6)
                    return "load_slot", sid

                if btns["delete"] and btns["delete"].handle_event(event):
                    if self.confirm_delete_slot == sid:
                        # Confirmed delete
                        delete_save(sid)
                        play_sfx('heavy_hit', 0.5)
                        self.confirm_delete_slot = None
                        self.refresh_slots()
                        return "none", None
                    else:
                        self.confirm_delete_slot = sid
                        play_sfx('click', 0.5)
                        self.refresh_slots()
                        return "none", None

                if btns["new"] and btns["new"].handle_event(event):
                    play_sfx('click', 0.6)
                    return "new_run_slot", sid

            # Clicking anywhere else cancels delete confirmation
            if self.confirm_delete_slot is not None:
                self.confirm_delete_slot = None
                self.refresh_slots()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_sfx('click', 0.5)
                return "back_to_title", None

        return "none", None

    def update(self, dt, mouse_pos):
        self.back_btn.update(mouse_pos)
        for btns in self.slot_buttons.values():
            if btns["load"]:
                btns["load"].update(mouse_pos)
            if btns["delete"]:
                btns["delete"].update(mouse_pos)
            if btns["new"]:
                btns["new"].update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)

        # Header Title
        title_surf = FONTS['huge'].render("SAVED EXPEDITIONS", True, COLOR_TEXT_GOLD)
        surface.blit(title_surf, title_surf.get_rect(center=(640, 52)))

        subtitle = FONTS['regular'].render("Select a saved journey to resume into the Crypt, or awaken a new hero", True, (190, 180, 210))
        surface.blit(subtitle, subtitle.get_rect(center=(640, 92)))

        # Draw Slot Cards
        for slot_info in self.slots:
            sid = slot_info["slot_id"]
            btn_dict = self.slot_buttons.get(sid)
            if not btn_dict:
                continue

            rect = btn_dict["rect"]

            if slot_info.get("exists"):
                # Active Save Slot
                char_id = slot_info.get("char_id", "blood_knight")
                accent_col = CHAR_COLORS.get(char_id, (180, 70, 90))

                # Card background
                pygame.draw.rect(surface, (28, 22, 36), rect, border_radius=12)
                pygame.draw.rect(surface, (70, 55, 85), rect, width=1, border_radius=12)

                # Header Banner in Class Color
                banner_rect = pygame.Rect(rect.x, rect.y, rect.width, 48)
                pygame.draw.rect(surface, accent_col, banner_rect, border_top_left_radius=12, border_top_right_radius=12)

                slot_txt = FONTS['bold'].render(f"SLOT {sid} — {slot_info.get('char_name', 'Hero').upper()}", True, (255, 255, 255))
                surface.blit(slot_txt, slot_txt.get_rect(center=banner_rect.center))

                # Class Title
                title_txt = FONTS['small'].render(slot_info.get("class_title", ""), True, (230, 215, 170))
                surface.blit(title_txt, title_txt.get_rect(center=(rect.centerx, rect.y + 68)))

                # Act & Floor Information
                act_str = f"Act {slot_info.get('act', 1)} • Floor {slot_info.get('current_floor', 1)}"
                act_surf = FONTS['medium'].render(act_str, True, COLOR_TEXT_GOLD)
                surface.blit(act_surf, act_surf.get_rect(center=(rect.centerx, rect.y + 102)))

                # Act Subtitle
                act_name = slot_info.get("act_title", "Crypt of the Necrolord")
                act_name_surf = FONTS['small'].render(act_name, True, (185, 175, 200))
                surface.blit(act_name_surf, act_name_surf.get_rect(center=(rect.centerx, rect.y + 128)))

                # Divider line
                pygame.draw.line(surface, (60, 48, 70), (rect.x + 20, rect.y + 148), (rect.right - 20, rect.y + 148), 1)

                # Player Health Bar
                hp = slot_info.get("hp", 0)
                max_hp = slot_info.get("max_hp", 1)
                HealthBar.draw(surface, rect.x + 40, rect.y + 165, rect.width - 80, 22, hp, max_hp, 0, font=FONTS['small'])

                # Gold with Coin Icon
                gy = rect.y + 205
                pygame.draw.circle(surface, (255, 215, 0), (rect.x + 48, gy + 10), 8)
                pygame.draw.circle(surface, (180, 140, 20), (rect.x + 48, gy + 10), 8, 1)
                gold_surf = FONTS['medium'].render(f"{slot_info.get('gold', 0)} Gold", True, COLOR_TEXT_GOLD)
                surface.blit(gold_surf, (rect.x + 65, gy))

                # Expedition Run Stats
                stats_y = rect.y + 242
                stat_lines = [
                    f"Cards in Deck:  {slot_info.get('deck_count', 0)}",
                    f"Relics Bound:   {slot_info.get('relic_count', 0)}",
                    f"Potions Ready:  {slot_info.get('potions_count', 0)}",
                ]
                for line in stat_lines:
                    lsurf = FONTS['small'].render(line, True, (200, 190, 215))
                    surface.blit(lsurf, (rect.x + 40, stats_y))
                    stats_y += 24

                # Timestamp
                time_y = rect.y + 328
                time_surf = FONTS['small'].render(f"Saved: {slot_info.get('timestamp', '')}", True, (135, 125, 145))
                surface.blit(time_surf, time_surf.get_rect(center=(rect.centerx, time_y)))

                # Action Buttons
                btn_dict["load"].draw(surface)
                btn_dict["delete"].draw(surface)

            else:
                # Empty Tomb Slot
                pygame.draw.rect(surface, (20, 16, 26), rect, border_radius=12)
                pygame.draw.rect(surface, (45, 38, 55), rect, width=1, border_radius=12)

                # Header Banner
                banner_rect = pygame.Rect(rect.x, rect.y, rect.width, 48)
                pygame.draw.rect(surface, (36, 30, 46), banner_rect, border_top_left_radius=12, border_top_right_radius=12)
                slot_txt = FONTS['bold'].render(f"SLOT {sid} — EMPTY GRAVE", True, (140, 130, 155))
                surface.blit(slot_txt, slot_txt.get_rect(center=banner_rect.center))

                # Hollow Crypt Motif
                center_y = rect.y + 190
                pygame.draw.circle(surface, (28, 22, 38), (rect.centerx, center_y), 45)
                pygame.draw.circle(surface, (55, 45, 70), (rect.centerx, center_y), 45, 2)
                
                # Sarcophagus / Tomb rune outline
                tomb_pts = [
                    (rect.centerx - 18, center_y - 25),
                    (rect.centerx + 18, center_y - 25),
                    (rect.centerx + 24, center_y + 25),
                    (rect.centerx - 24, center_y + 25)
                ]
                pygame.draw.polygon(surface, (70, 58, 85), tomb_pts, 2)

                empty_txt1 = FONTS['regular'].render("No Expedition In Progress", True, (160, 150, 175))
                surface.blit(empty_txt1, empty_txt1.get_rect(center=(rect.centerx, rect.y + 270)))

                empty_txt2 = FONTS['small'].render("Begin a new venture into the dark.", True, (115, 105, 130))
                surface.blit(empty_txt2, empty_txt2.get_rect(center=(rect.centerx, rect.y + 300)))

                # Start New Run Button
                btn_dict["new"].draw(surface)

        # Back Button
        self.back_btn.draw(surface)
