"""
Character Selection View: Select hero class before descending into the Crypt.
"""
import pygame
from engine.ui import Button
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, FONTS
)

CHARACTERS_DATA = [
    {
        "id": "blood_knight",
        "name": "BLOOD KNIGHT",
        "title": "Vanguard of Ruin",
        "hp": 80,
        "color": (210, 45, 60),
        "relic": "Burning Blood (Heal 6 HP)",
        "desc": [
            "Heavy armor & greatsword.",
            "Scales Strength, berserk self-harm",
            "buffs, & impenetrable Barricades."
        ],
        "starter_cards": "Strike x4, Defend x4, Bash, Iron Wave, Flex, Cleave"
    },
    {
        "id": "shadow_assassin",
        "name": "SHADOW ASSASSIN",
        "title": "Nightshade Weaver",
        "hp": 70,
        "color": (45, 185, 110),
        "relic": "Serpent Ring (+2 Draw Turn 1)",
        "desc": [
            "Twin venom daggers & stealth.",
            "Exponential Poison scaling,",
            "infinite Shivs & multi-hits."
        ],
        "starter_cards": "Strike x4, Defend x4, Neutralize, Poison, Dance, Step"
    },
    {
        "id": "void_necromancer",
        "name": "VOID NECROMANCER",
        "title": "Scion of the Abyss",
        "hp": 68,
        "color": (160, 70, 230),
        "relic": "Soul Phylactery (Exhaust 4 DMG)",
        "desc": [
            "Occult sacrificial rituals.",
            "Exhaust engines, Corpse",
            "Explosion, & 0-cost Corruption."
        ],
        "starter_cards": "Strike x4, Defend x4, Soul Drain, Offering, Explosion, Warcry"
    },
    {
        "id": "tempest_herald",
        "name": "TEMPEST HERALD",
        "title": "Conduit of Storms",
        "hp": 72,
        "color": (60, 170, 255),
        "relic": "Storm Core (End-turn 5 Zap)",
        "desc": [
            "Crackling lightning & glaciers.",
            "Surge energy manipulation,",
            "Vulnerable execution & Blizzard."
        ],
        "starter_cards": "Strike x4, Defend x4, Zap, Frost Barrier, Thunder Strike, Static"
    },
    {
        "id": "radiant_templar",
        "name": "RADIANT TEMPLAR",
        "title": "Champion of the Dawn",
        "hp": 85,
        "color": (245, 200, 60),
        "relic": "Sun Crest (Skills grant Thorns)",
        "desc": [
            "Gilded plate & sun mace.",
            "High HP, Retribution thorns,",
            "Consecration AoE, & Judgment."
        ],
        "starter_cards": "Strike x4, Defend x4, Smite, Holy Shield, Consecration, Vow"
    }
]

class CharSelectView:
    def __init__(self):
        self.selected_idx = 0
        self.start_btn = Button((520, 642, 240, 50), "EMBARK INTO THE CRYPT", FONTS['medium'], bg_color=(140, 35, 45), hover_color=(180, 45, 60))

    def handle_event(self, event, mouse_pos) -> tuple[str, str]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_btn.handle_event(event):
                selected_char = CHARACTERS_DATA[self.selected_idx]["id"]
                return "start_game", selected_char

            # Check card selections
            card_rects = self._get_char_card_rects()
            for idx, rect in enumerate(card_rects):
                if rect.collidepoint(event.pos):
                    if self.selected_idx != idx:
                        self.selected_idx = idx
                        play_sfx('click', 0.6)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_idx = (self.selected_idx - 1) % len(CHARACTERS_DATA)
                play_sfx('click', 0.5)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_idx = (self.selected_idx + 1) % len(CHARACTERS_DATA)
                play_sfx('click', 0.5)
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                idx = event.key - pygame.K_1
                if 0 <= idx < len(CHARACTERS_DATA):
                    self.selected_idx = idx
                    play_sfx('click', 0.5)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "start_game", CHARACTERS_DATA[self.selected_idx]["id"]

        return "none", ""

    def _get_char_card_rects(self):
        rects = []
        card_w = 230
        card_h = 485
        spacing = 244
        start_x = 38
        y = 135

        for i in range(len(CHARACTERS_DATA)):
            rects.append(pygame.Rect(start_x + i * spacing, y, card_w, card_h))
        return rects

    def update(self, dt, mouse_pos):
        self.start_btn.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)

        # Header Title
        title = FONTS['huge'].render("CHOOSE YOUR CHAMPION", True, COLOR_TEXT_GOLD)
        surface.blit(title, title.get_rect(center=(640, 52)))

        subtitle = FONTS['regular'].render("Select a hero class to descend into the perilous catacombs", True, (180, 170, 200))
        surface.blit(subtitle, subtitle.get_rect(center=(640, 92)))

        # Character Cards
        card_rects = self._get_char_card_rects()
        for i, (data, rect) in enumerate(zip(CHARACTERS_DATA, card_rects)):
            is_selected = (i == self.selected_idx)
            
            # Card Panel Background
            bg_color = (36, 26, 42) if not is_selected else (50, 36, 62)
            pygame.draw.rect(surface, bg_color, rect, border_radius=12)

            # Border
            border_color = data["color"] if is_selected else (65, 52, 75)
            border_width = 3 if is_selected else 1
            pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=12)

            # Class Header Banner
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 46)
            pygame.draw.rect(surface, data["color"], header_rect, border_top_left_radius=12, border_top_right_radius=12)
            
            c_name = FONTS['bold'].render(data["name"], True, (255, 255, 255))
            surface.blit(c_name, c_name.get_rect(center=header_rect.center))

            # Class Title
            c_title = FONTS['small'].render(data["title"], True, (240, 220, 150))
            surface.blit(c_title, c_title.get_rect(center=(rect.centerx, rect.y + 64)))

            # Health & Starting Stats
            hp_txt = FONTS['bold'].render(f"HP: {data['hp']}  |  3 Energy", True, (240, 80, 90))
            surface.blit(hp_txt, hp_txt.get_rect(center=(rect.centerx, rect.y + 96)))

            # Divider line
            pygame.draw.line(surface, (65, 52, 75), (rect.x + 15, rect.y + 118), (rect.right - 15, rect.y + 118), 1)

            # Starter Relic
            relic_title = FONTS['bold'].render("Relic:", True, COLOR_TEXT_GOLD)
            surface.blit(relic_title, (rect.x + 14, rect.y + 130))
            relic_name = FONTS['small'].render(data["relic"], True, (230, 220, 245))
            surface.blit(relic_name, (rect.x + 14, rect.y + 154))

            # Description Paragraph
            desc_title = FONTS['bold'].render("Fighting Style:", True, COLOR_TEXT_GOLD)
            surface.blit(desc_title, (rect.x + 14, rect.y + 190))

            dy = rect.y + 215
            for line in data["desc"]:
                d_surf = FONTS['small'].render(line, True, (200, 195, 215))
                surface.blit(d_surf, (rect.x + 14, dy))
                dy += 20

            # Starter Deck summary
            deck_title = FONTS['bold'].render("Starter Deck:", True, COLOR_TEXT_GOLD)
            surface.blit(deck_title, (rect.x + 14, rect.y + 295))
            deck_words = data["starter_cards"].split(", ")
            dky = rect.y + 320
            half = len(deck_words) // 2
            for dw in [deck_words[:half], deck_words[half:]]:
                dk_surf = FONTS['small'].render(", ".join(dw), True, (170, 160, 190))
                surface.blit(dk_surf, (rect.x + 14, dky))
                dky += 18

            # Selection Highlight indicator at bottom of card
            if is_selected:
                sel_box = pygame.Rect(rect.x + 30, rect.bottom - 44, rect.width - 60, 30)
                pygame.draw.rect(surface, data["color"], sel_box, border_radius=6)
                sel_txt = FONTS['bold'].render("SELECTED", True, (255, 255, 255))
                surface.blit(sel_txt, sel_txt.get_rect(center=sel_box.center))

        self.start_btn.draw(surface)

