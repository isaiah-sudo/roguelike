"""
Character Renderer: Detailed, handcrafted dark-fantasy vector art for Crypt of the Necrolord.
Reverts from AI bitmaps to the iconic OG geometric/vector procedural aesthetic,
upgraded with rich multi-tone shading, weapon bevels, pauldrons, glowing runic accents,
and smooth organic breathing animations.
"""
import math
import pygame
from typing import Optional

class CharacterRenderer:
    _instance = None

    def __init__(self):
        self._time = 0.0

    @classmethod
    def get(cls) -> 'CharacterRenderer':
        if cls._instance is None:
            cls._instance = CharacterRenderer()
        return cls._instance

    def update(self, dt: float):
        self._time += dt

    # =========================================================================
    # HEROES RENDERING
    # =========================================================================

    def draw_hero(self, surface: pygame.Surface, char_id: str, x: int, y: int, width: int, height: int, flash: bool = False):
        """Renders the detailed handcrafted vector hero with smooth breathing and drop shadow."""
        # Calm, smooth ease-in-out breathing curve
        t = self._time * 1.6
        breath = (math.sin(t) + 1.0) * 0.5
        smooth_b = breath * breath * (3.0 - 2.0 * breath)
        bob_y = -smooth_b * 3.5

        cx = x + width // 2
        feet_y = y + height

        # Soft drop shadow beneath feet
        self._draw_drop_shadow(surface, cx, feet_y, width=int(width * 0.75), height=20)

        # Temporary surface for crisp rendering and hit flash support
        surf_w = width + 60
        surf_h = height + 40
        char_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        # Local anchor: local_cx, local_feet_y
        lcx = surf_w // 2
        lfy = surf_h - 15 + int(bob_y)

        if char_id == "shadow_assassin":
            self._draw_vector_assassin(char_surf, lcx, lfy, width, height, t)
        elif char_id == "void_necromancer":
            self._draw_vector_necromancer(char_surf, lcx, lfy, width, height, t)
        elif char_id == "tempest_herald":
            self._draw_vector_tempest(char_surf, lcx, lfy, width, height, t)
        elif char_id == "radiant_templar":
            self._draw_vector_templar(char_surf, lcx, lfy, width, height, t)
        else: # blood_knight
            self._draw_vector_knight(char_surf, lcx, lfy, width, height, t)

        if flash:
            # Turn into bright white flash silhouette
            flash_surf = char_surf.copy()
            flash_surf.fill((255, 255, 255, 240), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_surf, (cx - surf_w // 2, y - 20))
        else:
            surface.blit(char_surf, (cx - surf_w // 2, y - 20))

    def _draw_drop_shadow(self, surface: pygame.Surface, cx: int, cy: int, width: int, height: int):
        s_surf = pygame.Surface((width + 20, height + 10), pygame.SRCALPHA)
        rect = pygame.Rect(10, 5, width, height)
        for i, a in enumerate([35, 70, 110]):
            inset = (2 - i) * 3
            r = rect.inflate(-inset * 2, -inset)
            pygame.draw.ellipse(s_surf, (10, 8, 14, a), r)
        surface.blit(s_surf, s_surf.get_rect(center=(cx, cy - 2)))

    # 1. BLOOD KNIGHT
    def _draw_vector_knight(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Heavy torn dark-crimson cloak (back layer)
        cloak_pts = [
            (cx, fy - 125),
            (cx + 42, fy - 4), (cx + 34, fy - 14), (cx + 25, fy - 2),
            (cx - 25, fy - 2), (cx - 34, fy - 14), (cx - 42, fy - 4)
        ]
        pygame.draw.polygon(s, (45, 18, 24), cloak_pts)
        pygame.draw.polygon(s, (80, 24, 32), cloak_pts, width=2)

        # Legs & Armored Greaves
        pygame.draw.rect(s, (32, 26, 32), (cx - 24, fy - 52, 18, 48), border_radius=4)
        pygame.draw.rect(s, (32, 26, 32), (cx + 6, fy - 52, 18, 48), border_radius=4)
        # Knee cops & Shin guards
        pygame.draw.rect(s, (65, 30, 36), (cx - 26, fy - 46, 20, 26), border_radius=3)
        pygame.draw.rect(s, (65, 30, 36), (cx + 4, fy - 46, 20, 26), border_radius=3)
        pygame.draw.line(s, (180, 45, 55), (cx - 16, fy - 44), (cx - 16, fy - 24), 2)
        pygame.draw.line(s, (180, 45, 55), (cx + 14, fy - 44), (cx + 14, fy - 24), 2)

        # Torso & Layered Obsidian Cuirass
        torso_rect = pygame.Rect(cx - 26, fy - 110, 52, 62)
        pygame.draw.rect(s, (28, 22, 28), torso_rect, border_radius=6)
        # Breastplate plates
        pygame.draw.polygon(s, (135, 32, 42), [
            (cx - 24, fy - 108), (cx + 24, fy - 108),
            (cx + 18, fy - 65), (cx, fy - 55), (cx - 18, fy - 65)
        ])
        pygame.draw.polygon(s, (190, 45, 58), [
            (cx - 24, fy - 108), (cx + 24, fy - 108),
            (cx + 18, fy - 65), (cx, fy - 55), (cx - 18, fy - 65)
        ], width=2)
        # Glowing crimson rune line on chest
        pygame.draw.line(s, (255, 60, 75), (cx, fy - 102), (cx, fy - 62), 3)
        pygame.draw.circle(s, (255, 120, 130), (cx, fy - 82), 4)

        # Heavy Spiked Pauldrons (Shoulders)
        # Left shoulder
        l_spikes = [(cx - 26, fy - 112), (cx - 46, fy - 124), (cx - 36, fy - 100)]
        pygame.draw.polygon(s, (110, 26, 35), l_spikes)
        pygame.draw.polygon(s, (220, 50, 65), l_spikes, width=2)
        # Right shoulder
        r_spikes = [(cx + 26, fy - 112), (cx + 46, fy - 124), (cx + 36, fy - 100)]
        pygame.draw.polygon(s, (110, 26, 35), r_spikes)
        pygame.draw.polygon(s, (220, 50, 65), r_spikes, width=2)

        # Spiked Great Helm
        head_y = fy - 128
        pygame.draw.circle(s, (36, 28, 36), (cx, head_y), 22)
        pygame.draw.circle(s, (80, 28, 38), (cx, head_y), 22, width=2)
        # Curved Demonic Horns
        pygame.draw.polygon(s, (140, 32, 42), [(cx - 14, head_y - 6), (cx - 32, head_y - 28), (cx - 18, head_y - 18)])
        pygame.draw.polygon(s, (220, 55, 68), [(cx - 14, head_y - 6), (cx - 32, head_y - 28), (cx - 18, head_y - 18)], width=1)
        pygame.draw.polygon(s, (140, 32, 42), [(cx + 14, head_y - 6), (cx + 32, head_y - 28), (cx + 18, head_y - 18)])
        pygame.draw.polygon(s, (220, 55, 68), [(cx + 14, head_y - 6), (cx + 32, head_y - 28), (cx + 18, head_y - 18)], width=1)
        # Fierce horizontal visor slit with blazing embers
        pygame.draw.line(s, (20, 15, 20), (cx - 14, head_y + 2), (cx + 14, head_y + 2), 4)
        pygame.draw.line(s, (255, 50, 65), (cx - 12, head_y + 2), (cx + 12, head_y + 2), 2)
        pygame.draw.circle(s, (255, 220, 200), (cx - 5, head_y + 2), 2)
        pygame.draw.circle(s, (255, 220, 200), (cx + 5, head_y + 2), 2)

        # Two-Handed Demonic Greatsword (held diagonally forward)
        p_hilt = (cx + 20, fy - 72)
        p_tip = (cx + 48, fy - 152)
        # Blade steel core
        pygame.draw.line(s, (180, 175, 185), p_hilt, p_tip, 8)
        # Dark fuller
        pygame.draw.line(s, (45, 20, 25), p_hilt, p_tip, 4)
        # Glowing crimson runic spine
        pygame.draw.line(s, (255, 65, 80), (cx + 24, fy - 84), (cx + 44, fy - 140), 2)
        # Crossguard
        pygame.draw.line(s, (210, 48, 62), (cx + 10, fy - 68), (cx + 30, fy - 76), 6)
        # Pommel
        pygame.draw.circle(s, (240, 180, 60), (cx + 16, fy - 62), 4)

    # 2. SHADOW ASSASSIN
    def _draw_vector_assassin(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Tattered Twin-Tail Shadow Cloak (Back)
        cloak_pts = [
            (cx, fy - 120),
            (cx + 36, fy - 6), (cx + 26, fy - 18), (cx + 12, fy - 4),
            (cx - 12, fy - 4), (cx - 26, fy - 18), (cx - 36, fy - 6)
        ]
        pygame.draw.polygon(s, (22, 45, 34), cloak_pts)
        pygame.draw.polygon(s, (45, 115, 80), cloak_pts, width=2)

        # Sleek dark leather trousers & boots
        pygame.draw.rect(s, (20, 28, 24), (cx - 20, fy - 50, 14, 46), border_radius=3)
        pygame.draw.rect(s, (20, 28, 24), (cx + 6, fy - 50, 14, 46), border_radius=3)
        # Straps on boots
        pygame.draw.line(s, (45, 160, 95), (cx - 20, fy - 30), (cx - 6, fy - 30), 2)
        pygame.draw.line(s, (45, 160, 95), (cx + 6, fy - 30), (cx + 20, fy - 30), 2)

        # Dark Leather Cuirass with crossed harnesses
        torso_rect = pygame.Rect(cx - 20, fy - 105, 40, 58)
        pygame.draw.rect(s, (28, 38, 32), torso_rect, border_radius=5)
        pygame.draw.rect(s, (45, 95, 68), torso_rect, width=2, border_radius=5)
        # Cross harness & emerald buckle
        pygame.draw.line(s, (55, 65, 58), (cx - 18, fy - 102), (cx + 18, fy - 60), 3)
        pygame.draw.line(s, (55, 65, 58), (cx + 18, fy - 102), (cx - 18, fy - 60), 3)
        pygame.draw.circle(s, (80, 245, 140), (cx, fy - 81), 4)

        # Hood & Deep Shadow Mask
        head_y = fy - 124
        # Cowl shape
        cowl_pts = [(cx, head_y - 20), (cx + 22, head_y + 12), (cx - 22, head_y + 12)]
        pygame.draw.polygon(s, (25, 55, 40), cowl_pts)
        pygame.draw.polygon(s, (50, 130, 85), cowl_pts, width=2)
        # Void inner shadow
        pygame.draw.ellipse(s, (12, 18, 14), (cx - 14, head_y - 4, 28, 20))
        # Twin glowing venom slit eyes
        pygame.draw.polygon(s, (90, 255, 150), [(cx - 10, head_y + 4), (cx - 4, head_y + 2), (cx - 5, head_y + 6)])
        pygame.draw.polygon(s, (90, 255, 150), [(cx + 10, head_y + 4), (cx + 4, head_y + 2), (cx + 5, head_y + 6)])
        pygame.draw.circle(s, (220, 255, 230), (cx - 7, head_y + 4), 1)
        pygame.draw.circle(s, (220, 255, 230), (cx + 7, head_y + 4), 1)

        # Dual Serrated Venom Daggers
        # Right Hand Dagger (Forward strike)
        d1_p1 = (cx + 22, fy - 70)
        d1_p2 = (cx + 48, fy - 110)
        pygame.draw.line(s, (180, 195, 185), d1_p1, d1_p2, 4)
        pygame.draw.line(s, (70, 255, 140), (cx + 26, fy - 76), d1_p2, 2)
        pygame.draw.circle(s, (70, 255, 140), (cx + 50, fy - 106), 2) # poison drip

        # Left Hand Dagger (Reverse grip)
        d2_p1 = (cx - 20, fy - 74)
        d2_p2 = (cx - 38, fy - 38)
        pygame.draw.line(s, (180, 195, 185), d2_p1, d2_p2, 4)
        pygame.draw.line(s, (70, 255, 140), (cx - 24, fy - 68), d2_p2, 2)
        pygame.draw.circle(s, (70, 255, 140), (cx - 39, fy - 34), 2)

    # 3. VOID NECROMANCER
    def _draw_vector_necromancer(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Flowing jagged sorcerer mantle with runic trim
        robe_pts = [
            (cx, fy - 120),
            (cx + 38, fy - 2), (cx + 26, fy - 14), (cx + 12, fy - 2),
            (cx - 12, fy - 2), (cx - 26, fy - 14), (cx - 38, fy - 2)
        ]
        pygame.draw.polygon(s, (38, 20, 52), robe_pts)
        pygame.draw.polygon(s, (135, 60, 185), robe_pts, width=2)

        # Inner dark tunic with void glyphs
        tunic = pygame.Rect(cx - 18, fy - 105, 36, 62)
        pygame.draw.rect(s, (24, 14, 34), tunic, border_radius=4)
        pygame.draw.line(s, (190, 80, 255), (cx, fy - 98), (cx, fy - 55), 2)
        for gy in [fy - 88, fy - 74, fy - 62]:
            pygame.draw.line(s, (190, 80, 255), (cx - 6, gy), (cx + 6, gy), 2)

        # Flared High Sorcerer Collar
        pygame.draw.polygon(s, (90, 40, 130), [(cx - 24, fy - 110), (cx - 34, fy - 132), (cx - 16, fy - 118)])
        pygame.draw.polygon(s, (90, 40, 130), [(cx + 24, fy - 110), (cx + 34, fy - 132), (cx + 16, fy - 118)])

        # Horned Bone Skull Mask
        head_y = fy - 126
        # Skull base
        pygame.draw.circle(s, (225, 218, 230), (cx, head_y), 20)
        pygame.draw.circle(s, (160, 150, 175), (cx, head_y), 20, width=2)
        # Deep hollow eye sockets with violet soul flame
        pygame.draw.circle(s, (25, 10, 38), (cx - 6, head_y), 5)
        pygame.draw.circle(s, (25, 10, 38), (cx + 6, head_y), 5)
        pygame.draw.circle(s, (215, 100, 255), (cx - 6, head_y), 2)
        pygame.draw.circle(s, (215, 100, 255), (cx + 6, head_y), 2)
        # Nasal cavity
        pygame.draw.polygon(s, (25, 10, 38), [(cx, head_y + 4), (cx - 2, head_y + 8), (cx + 2, head_y + 8)])
        # Curved Skeletal Horns
        pygame.draw.polygon(s, (170, 160, 185), [(cx - 12, head_y - 8), (cx - 30, head_y - 28), (cx - 18, head_y - 18)])
        pygame.draw.polygon(s, (170, 160, 185), [(cx + 12, head_y - 8), (cx + 30, head_y - 28), (cx + 18, head_y - 18)])

        # Occult Soul Staff (Right Hand)
        staff_base = (cx + 32, fy - 4)
        staff_top = (cx + 32, fy - 150)
        pygame.draw.line(s, (85, 70, 95), staff_base, staff_top, 4)
        # Gnarled staff crook
        pygame.draw.arc(s, (140, 110, 160), (cx + 20, fy - 164, 24, 24), 0, math.pi * 1.5, 3)
        # Pulsing Violet Soul Orb atop staff
        pulse = math.sin(t * 3.0) * 2.0
        orb_center = (cx + 32, fy - 150)
        pygame.draw.circle(s, (180, 60, 255), orb_center, int(11 + pulse))
        pygame.draw.circle(s, (240, 180, 255), orb_center, int(6 + pulse * 0.5))
        pygame.draw.circle(s, (255, 255, 255), orb_center, 3)

    # 4. TEMPEST HERALD
    def _draw_vector_tempest(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Deep sapphire & navy storm robes
        robe_pts = [
            (cx, fy - 122),
            (cx + 36, fy - 4), (cx + 24, fy - 16), (cx + 10, fy - 4),
            (cx - 10, fy - 4), (cx - 24, fy - 16), (cx - 36, fy - 4)
        ]
        pygame.draw.polygon(s, (20, 36, 68), robe_pts)
        pygame.draw.polygon(s, (65, 175, 255), robe_pts, width=2)

        # Storm breast medallion & electric runes
        cuirass = pygame.Rect(cx - 20, fy - 106, 40, 58)
        pygame.draw.rect(s, (26, 48, 85), cuirass, border_radius=5)
        pygame.draw.rect(s, (80, 195, 255), cuirass, width=2, border_radius=5)
        # Lightning glyph on chest
        lg_pts = [(cx - 2, fy - 98), (cx + 8, fy - 84), (cx + 1, fy - 84), (cx + 6, fy - 68), (cx - 6, fy - 80), (cx, fy - 80)]
        pygame.draw.polygon(s, (255, 255, 255), lg_pts)
        pygame.draw.polygon(s, (80, 220, 255), lg_pts, width=1)

        # Sorcerer Hood & Electric Eyes
        head_y = fy - 124
        hood_pts = [(cx, head_y - 20), (cx + 20, head_y + 12), (cx - 20, head_y + 12)]
        pygame.draw.polygon(s, (24, 46, 85), hood_pts)
        pygame.draw.polygon(s, (70, 180, 255), hood_pts, width=2)
        # Inner shadow
        pygame.draw.ellipse(s, (10, 20, 40), (cx - 14, head_y - 2, 28, 18))
        # Electric Cyan Eyes
        pygame.draw.circle(s, (100, 240, 255), (cx - 6, head_y + 6), 3)
        pygame.draw.circle(s, (100, 240, 255), (cx + 6, head_y + 6), 3)
        pygame.draw.circle(s, (255, 255, 255), (cx - 6, head_y + 6), 1)
        pygame.draw.circle(s, (255, 255, 255), (cx + 6, head_y + 6), 1)

        # Levitating Storm Catalyst Crystal (Right Hand)
        c_x = cx + 38
        c_y = fy - 92 + int(math.sin(t * 3.5) * 4)
        # Diamond crystal
        crystal_pts = [(c_x, c_y - 15), (c_x + 9, c_y), (c_x, c_y + 15), (c_x - 9, c_y)]
        pygame.draw.polygon(s, (120, 220, 255), crystal_pts)
        pygame.draw.polygon(s, (255, 255, 255), crystal_pts, width=2)
        # Crackling lightning sparks
        spark_phase = int(t * 12) % 3
        if spark_phase == 0:
            pygame.draw.line(s, (255, 255, 255), (c_x - 12, c_y - 8), (c_x - 4, c_y), 2)
            pygame.draw.line(s, (80, 220, 255), (c_x + 4, c_y), (c_x + 14, c_y + 8), 2)
        else:
            pygame.draw.line(s, (255, 255, 255), (c_x + 10, c_y - 10), (c_x + 3, c_y), 2)
            pygame.draw.line(s, (80, 220, 255), (c_x - 3, c_y), (c_x - 12, c_y + 10), 2)

    # 5. RADIANT TEMPLAR
    def _draw_vector_templar(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # White & Golden Knight's Tabard (Back)
        tabard_pts = [
            (cx, fy - 124),
            (cx + 34, fy - 6), (cx + 22, fy - 14), (cx + 8, fy - 6),
            (cx - 8, fy - 6), (cx - 22, fy - 14), (cx - 34, fy - 6)
        ]
        pygame.draw.polygon(s, (75, 62, 35), tabard_pts)
        pygame.draw.polygon(s, (220, 180, 50), tabard_pts, width=2)

        # Armored Greaves & Sabatons
        pygame.draw.rect(s, (45, 40, 30), (cx - 22, fy - 52, 16, 48), border_radius=4)
        pygame.draw.rect(s, (45, 40, 30), (cx + 6, fy - 52, 16, 48), border_radius=4)
        pygame.draw.rect(s, (200, 165, 50), (cx - 24, fy - 46, 18, 24), border_radius=3)
        pygame.draw.rect(s, (200, 165, 50), (cx + 6, fy - 46, 18, 24), border_radius=3)

        # Gilded Breastplate
        torso = pygame.Rect(cx - 24, fy - 108, 48, 60)
        pygame.draw.rect(s, (52, 45, 28), torso, border_radius=6)
        pygame.draw.polygon(s, (215, 180, 55), [
            (cx - 22, fy - 106), (cx + 22, fy - 106),
            (cx + 16, fy - 64), (cx, fy - 54), (cx - 16, fy - 64)
        ])
        pygame.draw.polygon(s, (255, 235, 140), [
            (cx - 22, fy - 106), (cx + 22, fy - 106),
            (cx + 16, fy - 64), (cx, fy - 54), (cx - 16, fy - 64)
        ], width=2)
        # Holy Sun Cross on Chest
        pygame.draw.circle(s, (255, 245, 190), (cx, fy - 80), 7)
        pygame.draw.line(s, (255, 245, 190), (cx - 11, fy - 80), (cx + 11, fy - 80), 3)
        pygame.draw.line(s, (255, 245, 190), (cx, fy - 91), (cx, fy - 69), 3)

        # Massive Golden Pauldrons
        pygame.draw.circle(s, (210, 175, 45), (cx - 28, fy - 112), 14)
        pygame.draw.circle(s, (255, 230, 120), (cx - 28, fy - 112), 14, width=2)
        pygame.draw.circle(s, (210, 175, 45), (cx + 28, fy - 112), 14)
        pygame.draw.circle(s, (255, 230, 120), (cx + 28, fy - 112), 14, width=2)

        # Templar Great Helm
        head_y = fy - 128
        pygame.draw.circle(s, (180, 150, 45), (cx, head_y), 24)
        pygame.draw.circle(s, (245, 215, 95), (cx, head_y), 24, width=2)
        # Golden Cross Visor
        pygame.draw.line(s, (255, 245, 180), (cx - 14, head_y), (cx + 14, head_y), 4)
        pygame.draw.line(s, (255, 245, 180), (cx, head_y - 14), (cx, head_y + 14), 4)
        pygame.draw.circle(s, (255, 255, 255), (cx, head_y), 4)

        # Holy Sun Warhammer (Right Hand)
        mace_p1 = (cx + 30, fy - 30)
        mace_p2 = (cx + 42, fy - 138)
        pygame.draw.line(s, (140, 120, 80), mace_p1, mace_p2, 6)
        # Heavy radiant hammer head
        mhead_rect = pygame.Rect(cx + 30, fy - 150, 24, 20)
        pygame.draw.rect(s, (255, 215, 60), mhead_rect, border_radius=4)
        pygame.draw.rect(s, (255, 245, 160), mhead_rect, width=2, border_radius=4)
        # Sunburst aura around hammer head
        pygame.draw.circle(s, (255, 230, 100), mhead_rect.center, 5)

        # Sun Tower Shield (Left Hand)
        shield_pts = [
            (cx - 38, fy - 105), (cx - 20, fy - 105),
            (cx - 18, fy - 52), (cx - 29, fy - 36), (cx - 40, fy - 52)
        ]
        pygame.draw.polygon(s, (190, 155, 45), shield_pts)
        pygame.draw.polygon(s, (255, 235, 130), shield_pts, width=2)
        pygame.draw.circle(s, (255, 240, 160), (cx - 29, fy - 72), 6)

    # =========================================================================
    # ENEMIES RENDERING
    # =========================================================================

    def draw_enemy(self, surface: pygame.Surface, enemy, x: int, y: int, width: int, height: int, flash: bool = False):
        """Renders the detailed handcrafted vector enemy with organic breathing and drop shadow."""
        phase = (x % 500) / 100.0
        t = self._time * 1.6 + phase
        breath = (math.sin(t) + 1.0) * 0.5
        smooth_b = breath * breath * (3.0 - 2.0 * breath)
        bob_y = -smooth_b * 3.0

        cx = x + width // 2
        feet_y = y + height

        # Shadow
        self._draw_drop_shadow(surface, cx, feet_y, width=int(width * 0.8), height=22)

        surf_w = width + 80
        surf_h = height + 60
        char_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        lcx = surf_w // 2
        lfy = surf_h - 15 + int(bob_y)

        name = getattr(enemy, 'name', '')
        cls_name = enemy.__class__.__name__

        if "Malakor" in name or getattr(enemy, 'is_boss', False):
            self._draw_vector_boss_malakor(char_surf, lcx, lfy, width, height, t)
        elif "Spider" in name or "Bat" in name or "Rat" in name:
            self._draw_vector_dread_spider(char_surf, lcx, lfy, width, height, t)
        elif "Sentinel" in name or "Skeleton" in name or "Wight" in name:
            self._draw_vector_skeleton_sentinel(char_surf, lcx, lfy, width, height, t)
        elif "Reaver" in name or "Demon" in name or "Archon" in name or "Hound" in name:
            self._draw_vector_void_reaver(char_surf, lcx, lfy, width, height, t)
        else: # Cultist, Alchemist, Hierophant, etc.
            self._draw_vector_cultist(char_surf, lcx, lfy, width, height, t)

        if flash:
            flash_surf = char_surf.copy()
            flash_surf.fill((255, 255, 255, 240), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_surf, (cx - surf_w // 2, y - 30))
        else:
            surface.blit(char_surf, (cx - surf_w // 2, y - 30))

    # 1. CULTIST
    def _draw_vector_cultist(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Ragged cultist robes
        robe_pts = [
            (cx, fy - 110),
            (cx + 34, fy - 2), (cx + 20, fy - 12), (cx + 6, fy - 2),
            (cx - 6, fy - 2), (cx - 20, fy - 12), (cx - 34, fy - 2)
        ]
        pygame.draw.polygon(s, (52, 22, 26), robe_pts)
        pygame.draw.polygon(s, (160, 48, 55), robe_pts, width=2)

        # Occult skull amulet
        pygame.draw.line(s, (90, 80, 75), (cx - 10, fy - 90), (cx, fy - 75), 2)
        pygame.draw.line(s, (90, 80, 75), (cx + 10, fy - 90), (cx, fy - 75), 2)
        pygame.draw.circle(s, (220, 215, 210), (cx, fy - 73), 5)

        # Deep Hood & Glowing Red Eyes
        head_y = fy - 115
        hood_pts = [(cx, head_y - 18), (cx + 20, head_y + 12), (cx - 20, head_y + 12)]
        pygame.draw.polygon(s, (65, 26, 32), hood_pts)
        pygame.draw.polygon(s, (180, 50, 60), hood_pts, width=2)
        pygame.draw.ellipse(s, (18, 10, 14), (cx - 13, head_y - 2, 26, 18))
        # Sinister Red Eyes
        pygame.draw.circle(s, (255, 55, 65), (cx - 6, head_y + 6), 3)
        pygame.draw.circle(s, (255, 55, 65), (cx + 6, head_y + 6), 3)

        # Curved Sacrificial Dagger (held pointing forward left)
        d_p1 = (cx - 18, fy - 62)
        d_p2 = (cx - 42, fy - 82)
        pygame.draw.line(s, (210, 205, 215), d_p1, d_p2, 4)
        pygame.draw.line(s, (255, 60, 75), d_p1, d_p2, 2)
        # Runic occult book in other hand
        book = pygame.Rect(cx + 12, fy - 75, 22, 28)
        pygame.draw.rect(s, (45, 30, 24), book, border_radius=3)
        pygame.draw.rect(s, (220, 180, 70), book, width=1, border_radius=3)
        pygame.draw.line(s, (255, 70, 70), (cx + 20, fy - 68), (cx + 26, fy - 62), 2)

    # 2. SKELETON SENTINEL
    def _draw_vector_skeleton_sentinel(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Ribcage & Spine
        pygame.draw.line(s, (210, 200, 190), (cx, fy - 95), (cx, fy - 40), 4)
        for ry in [fy - 85, fy - 75, fy - 65, fy - 55]:
            pygame.draw.line(s, (190, 185, 175), (cx - 14, ry), (cx + 14, ry), 3)

        # Rusted Iron Tassets & Hip Armor
        pygame.draw.polygon(s, (55, 48, 52), [(cx - 16, fy - 45), (cx + 16, fy - 45), (cx, fy - 28)])
        pygame.draw.polygon(s, (130, 95, 60), [(cx - 16, fy - 45), (cx + 16, fy - 45), (cx, fy - 28)], width=2)

        # Cracked Skull
        head_y = fy - 114
        pygame.draw.circle(s, (225, 215, 200), (cx, head_y), 19)
        # Eye sockets & Glowing Red Pinpoints
        pygame.draw.circle(s, (24, 18, 22), (cx - 6, head_y + 1), 5)
        pygame.draw.circle(s, (24, 18, 22), (cx + 6, head_y + 1), 5)
        pygame.draw.circle(s, (255, 50, 60), (cx - 6, head_y + 1), 2)
        pygame.draw.circle(s, (255, 50, 60), (cx + 6, head_y + 1), 2)
        # Jaw & teeth
        pygame.draw.rect(s, (210, 200, 185), (cx - 8, head_y + 12, 16, 9), border_radius=2)
        pygame.draw.line(s, (45, 35, 40), (cx - 6, head_y + 16), (cx + 6, head_y + 16), 1)

        # Spiked Round Shield (Left Hand, facing player)
        s_cx = cx - 26
        s_cy = fy - 65
        pygame.draw.circle(s, (52, 45, 50), (s_cx, s_cy), 22)
        pygame.draw.circle(s, (140, 100, 65), (s_cx, s_cy), 22, width=3)
        pygame.draw.circle(s, (210, 195, 180), (s_cx, s_cy), 6) # shield boss spike

        # Notched Broadsword (Right Hand)
        sw_p1 = (cx + 18, fy - 40)
        sw_p2 = (cx + 42, fy - 118)
        pygame.draw.line(s, (170, 165, 175), sw_p1, sw_p2, 6)
        pygame.draw.line(s, (230, 225, 235), sw_p1, sw_p2, 2)
        pygame.draw.line(s, (90, 75, 60), (cx + 10, fy - 48), (cx + 26, fy - 42), 5)

    # 3. DREAD SPIDER
    def _draw_vector_dread_spider(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Spiky arachnid legs (8 legs)
        leg_col = (45, 65, 50)
        for i, lx in enumerate([-35, -20, 20, 35]):
            joint_y = fy - 65 - abs(lx) // 3
            foot_y = fy - 4
            # Knee up, tip down
            pygame.draw.line(s, leg_col, (cx + (lx // 2), fy - 45), (cx + lx * 1.3, joint_y), 3)
            pygame.draw.line(s, (70, 120, 85), (cx + lx * 1.3, joint_y), (cx + lx * 1.4, foot_y), 3)

        # Bulging venomous abdomen (Back)
        pygame.draw.ellipse(s, (32, 48, 38), (cx - 26, fy - 85, 52, 42))
        pygame.draw.ellipse(s, (55, 130, 85), (cx - 26, fy - 85, 52, 42), width=2)
        # Toxic green hazard markings
        pygame.draw.line(s, (80, 245, 140), (cx - 12, fy - 68), (cx, fy - 58), 2)
        pygame.draw.line(s, (80, 245, 140), (cx + 12, fy - 68), (cx, fy - 58), 2)

        # Cephalothorax (Front Head)
        pygame.draw.circle(s, (22, 34, 26), (cx, fy - 52), 18)
        pygame.draw.circle(s, (45, 95, 65), (cx, fy - 52), 18, width=2)

        # Multi-cluster glowing crimson eyes
        for ex, ey in [(-8, fy - 56), (-3, fy - 58), (3, fy - 58), (8, fy - 56), (-5, fy - 50), (5, fy - 50)]:
            pygame.draw.circle(s, (255, 45, 55), (cx + ex, ey), 2)

        # Dripping venomous fangs
        pygame.draw.polygon(s, (210, 215, 200), [(cx - 8, fy - 40), (cx - 5, fy - 40), (cx - 6, fy - 26)])
        pygame.draw.polygon(s, (210, 215, 200), [(cx + 8, fy - 40), (cx + 5, fy - 40), (cx + 6, fy - 26)])
        pygame.draw.circle(s, (75, 255, 130), (cx - 6, fy - 24), 2)
        pygame.draw.circle(s, (75, 255, 130), (cx + 6, fy - 24), 2)

    # 4. VOID REAVER
    def _draw_vector_void_reaver(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Hulking obsidian demon muscular torso
        torso = pygame.Rect(cx - 30, fy - 110, 60, 65)
        pygame.draw.rect(s, (26, 18, 34), torso, border_radius=8)
        pygame.draw.rect(s, (140, 50, 185), torso, width=2, border_radius=8)
        # Glowing void core in chest
        pygame.draw.circle(s, (180, 55, 240), (cx, fy - 82), 12)
        pygame.draw.circle(s, (245, 190, 255), (cx, fy - 82), 6)

        # Spiked obsidian shoulders
        pygame.draw.polygon(s, (75, 30, 100), [(cx - 30, fy - 110), (cx - 50, fy - 128), (cx - 38, fy - 96)])
        pygame.draw.polygon(s, (75, 30, 100), [(cx + 30, fy - 110), (cx + 50, fy - 128), (cx + 38, fy - 96)])

        # Demonic Head & Four Horns
        head_y = fy - 122
        pygame.draw.circle(s, (32, 20, 42), (cx, head_y), 20)
        # Inner horns
        pygame.draw.polygon(s, (140, 45, 190), [(cx - 8, head_y - 8), (cx - 24, head_y - 34), (cx - 15, head_y - 20)])
        pygame.draw.polygon(s, (140, 45, 190), [(cx + 8, head_y - 8), (cx + 24, head_y - 34), (cx + 15, head_y - 20)])
        # Outer horns
        pygame.draw.polygon(s, (95, 35, 130), [(cx - 16, head_y), (cx - 38, head_y - 18), (cx - 20, head_y - 10)])
        pygame.draw.polygon(s, (95, 35, 130), [(cx + 16, head_y), (cx + 38, head_y - 18), (cx + 20, head_y - 10)])
        # Glowing violet demon eyes
        pygame.draw.polygon(s, (230, 120, 255), [(cx - 10, head_y + 4), (cx - 4, head_y + 1), (cx - 5, head_y + 7)])
        pygame.draw.polygon(s, (230, 120, 255), [(cx + 10, head_y + 4), (cx + 4, head_y + 1), (cx + 5, head_y + 7)])

        # Massive Claws wreathed in void fire
        pygame.draw.circle(s, (160, 40, 220), (cx - 36, fy - 50), 10)
        pygame.draw.line(s, (240, 180, 255), (cx - 44, fy - 52), (cx - 48, fy - 38), 3)
        pygame.draw.line(s, (240, 180, 255), (cx - 38, fy - 52), (cx - 38, fy - 34), 3)
        pygame.draw.line(s, (240, 180, 255), (cx - 32, fy - 52), (cx - 28, fy - 38), 3)

    # 5. BOSS: NECROLORD MALAKOR
    def _draw_vector_boss_malakor(self, s: pygame.Surface, cx: int, fy: int, w: int, h: int, t: float):
        # Tattered sovereign dark-frost robes (hovering floating baseline)
        float_y = int(math.sin(t * 2.0) * 6)
        cy_adj = fy + float_y

        robe_pts = [
            (cx, cy_adj - 150),
            (cx + 48, cy_adj - 6), (cx + 34, cy_adj - 22), (cx + 16, cy_adj - 8),
            (cx - 16, cy_adj - 8), (cx - 34, cy_adj - 22), (cx - 48, cy_adj - 6)
        ]
        pygame.draw.polygon(s, (22, 16, 32), robe_pts)
        pygame.draw.polygon(s, (80, 210, 230), robe_pts, width=2)

        # Ribcage & Frost Core
        pygame.draw.circle(s, (70, 220, 240), (cx, cy_adj - 105), 14)
        pygame.draw.circle(s, (230, 250, 255), (cx, cy_adj - 105), 7)
        for ry in [cy_adj - 118, cy_adj - 108, cy_adj - 98, cy_adj - 88]:
            pygame.draw.line(s, (210, 205, 215), (cx - 18, ry), (cx + 18, ry), 3)

        # Ornate Spiked Bone & Ice Crown
        head_y = cy_adj - 150
        pygame.draw.circle(s, (235, 230, 240), (cx, head_y), 22)
        # Eye sockets & Cyan Soul Eyes
        pygame.draw.circle(s, (14, 20, 30), (cx - 7, head_y + 2), 6)
        pygame.draw.circle(s, (14, 20, 30), (cx + 7, head_y + 2), 6)
        pygame.draw.circle(s, (80, 240, 255), (cx - 7, head_y + 2), 3)
        pygame.draw.circle(s, (80, 240, 255), (cx + 7, head_y + 2), 3)

        # Sovereign Crown
        crown_pts = [
            (cx - 20, head_y - 12),
            (cx - 26, head_y - 36),
            (cx - 10, head_y - 24),
            (cx, head_y - 44),
            (cx + 10, head_y - 24),
            (cx + 26, head_y - 36),
            (cx + 20, head_y - 12)
        ]
        pygame.draw.polygon(s, (235, 200, 75), crown_pts)
        pygame.draw.polygon(s, (255, 245, 160), crown_pts, width=2)
        # Crown jewels
        pygame.draw.circle(s, (80, 230, 255), (cx, head_y - 30), 4)

        # Skeletal Death Scepter with Cyan Soul Flame
        s_p1 = (cx + 40, cy_adj - 12)
        s_p2 = (cx + 40, cy_adj - 185)
        pygame.draw.line(s, (130, 120, 140), s_p1, s_p2, 5)
        # Skull head on staff
        skull_top = (cx + 40, cy_adj - 185)
        pygame.draw.circle(s, (230, 225, 235), skull_top, 10)
        # Soul Fire Flare atop staff
        flame_pulse = math.sin(t * 4.0) * 3
        pygame.draw.circle(s, (60, 220, 255), (skull_top[0], skull_top[1] - 8), int(12 + flame_pulse))
        pygame.draw.circle(s, (220, 250, 255), (skull_top[0], skull_top[1] - 8), 5)

    # =========================================================================
    # HEAD Y FOR INTENT
    # =========================================================================

    def get_enemy_head_y(self, enemy, y: int, height: int) -> int:
        """Calculates exact top coordinate of enemy head so intent NEVER clips."""
        if getattr(enemy, 'is_boss', False):
            # Boss has tall crown and hovering posture
            return y - 48
        elif getattr(enemy, 'is_elite', False):
            return y - 25
        return y - 10

    # =========================================================================
    # CHARACTER SELECTION PORTRAITS
    # =========================================================================

    def draw_hero_portrait(self, surface: pygame.Surface, char_id: str, rect: pygame.Rect):
        """Renders crisp, styled vector portrait for the character select cards."""
        # Dark pane backdrop
        pygame.draw.rect(surface, (20, 16, 26), rect, border_radius=6)

        # Draw framed upper-body of the hero centered in the rect
        cx = rect.centerx
        fy = rect.bottom + 36 # anchored so head and shoulders fill the portrait frame
        w = 110
        h = 140

        # Clip rendering to the portrait rectangle
        orig_clip = surface.get_clip()
        surface.set_clip(rect)

        # Render vector hero in portrait frame
        if char_id == "shadow_assassin":
            self._draw_vector_assassin(surface, cx, fy, w, h, 0.0)
        elif char_id == "void_necromancer":
            self._draw_vector_necromancer(surface, cx, fy, w, h, 0.0)
        elif char_id == "tempest_herald":
            self._draw_vector_tempest(surface, cx, fy, w, h, 0.0)
        elif char_id == "radiant_templar":
            self._draw_vector_templar(surface, cx, fy, w, h, 0.0)
        else: # blood_knight
            self._draw_vector_knight(surface, cx, fy, w, h, 0.0)

        # Restore clip
        surface.set_clip(orig_clip)

        # Subtle inner border
        pygame.draw.rect(surface, (65, 52, 75), rect, width=1, border_radius=6)
