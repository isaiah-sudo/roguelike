"""
Sprite Manager: High-fidelity 2D Dark Fantasy Sprite Loader and Animator.
Handles caching, aspect-ratio scaling, smooth idle breathing, hit flashes,
and drop shadows for heroes and enemies in Crypt of the Necrolord.
"""
import os
import sys
import math
import pygame
from typing import Optional

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    ASSETS_DIR = os.path.join(sys._MEIPASS, "assets")
else:
    ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
CHAR_SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites", "characters")
ENEMY_SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites", "enemies")
PORTRAITS_DIR = os.path.join(ASSETS_DIR, "portraits")
CARDS_DIR = os.path.join(ASSETS_DIR, "cards")

# Enemy class/name mapping to available sprite keys
ENEMY_SPRITE_MAP = {
    # Undead
    "CryptCultist": "cultist",
    "Cultist": "cultist",
    "DarkWarlock": "cultist",
    "CorruptedHierophant": "cultist",
    "MadAlchemist": "cultist",
    "SkeletonSentinel": "skeleton_sentinel",
    "Skeletal Sentinel": "skeleton_sentinel",
    "TormentedWight": "skeleton_sentinel",
    "VoidRevenant": "skeleton_sentinel",

    # Beasts
    "DreadSpider": "dread_spider",
    "Dread Spider": "dread_spider",
    "PlagueRat": "dread_spider",
    "Plague Fiend": "dread_spider",
    "BloodBat": "dread_spider",
    "InfernalHound": "void_reaver",

    # Demons / Automatons
    "VoidReaver": "void_reaver",
    "CinderDemon": "void_reaver",
    "FlameArchon": "void_reaver",
    "NemesisAvatar": "void_reaver",
    "CenturionAutomaton": "void_reaver",
    "ObsidianGolem": "void_reaver",

    # Bosses
    "NecrolordMalakor": "necrolord_malakor",
    "VoidBehemoth": "necrolord_malakor",
    "IgnisTheInfernal": "necrolord_malakor",
    "TheCorruptedHeart": "necrolord_malakor",
    "ArchmageValerius": "necrolord_malakor",
}

class SpriteManager:
    _instance = None

    def __init__(self):
        self._sprite_cache: dict[str, pygame.Surface] = {}
        self._flash_cache: dict[str, pygame.Surface] = {}
        self._portraits_cache: dict[str, pygame.Surface] = {}
        self._cards_cache: dict[str, pygame.Surface] = {}
        self._shadow_cache: dict[tuple[int, int], pygame.Surface] = {}
        self._time = 0.0

    @classmethod
    def get(cls) -> 'SpriteManager':
        if cls._instance is None:
            cls._instance = SpriteManager()
        return cls._instance

    def update(self, dt: float):
        self._time += dt

    def _load_image(self, path: str) -> pygame.Surface:
        raw = pygame.image.load(path)
        if pygame.display.get_surface() is not None:
            return raw.convert_alpha()
        return raw

    def get_portrait(self, char_id: str, size: tuple[int, int] = (200, 115)) -> Optional[pygame.Surface]:
        cache_key = f"{char_id}_{size[0]}x{size[1]}"
        if cache_key in self._portraits_cache:
            return self._portraits_cache[cache_key]

        path = os.path.join(PORTRAITS_DIR, f"{char_id}.png")
        if not os.path.exists(path):
            return None

        try:
            raw = self._load_image(path)
            scaled = pygame.transform.smoothscale(raw, size)
            self._portraits_cache[cache_key] = scaled
            return scaled
        except Exception as e:
            print(f"[SpriteManager] Error loading portrait {char_id}: {e}")
            return None

    def get_card_art(self, card_id: str, size: tuple[int, int] = (130, 64)) -> Optional[pygame.Surface]:
        cache_key = f"{card_id}_{size[0]}x{size[1]}"
        if cache_key in self._cards_cache:
            return self._cards_cache[cache_key]

        path = os.path.join(CARDS_DIR, f"{card_id}.png")
        if not os.path.exists(path):
            return None

        try:
            raw = self._load_image(path)
            scaled = pygame.transform.smoothscale(raw, size)

            # Round the corners with SRCALPHA mask
            mask_surf = pygame.Surface(size, pygame.SRCALPHA)
            mask_surf.fill((0, 0, 0, 0))
            pygame.draw.rect(mask_surf, (255, 255, 255, 255), (0, 0, size[0], size[1]), border_radius=6)
            scaled.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            self._cards_cache[cache_key] = scaled
            return scaled
        except Exception as e:
            print(f"[SpriteManager] Error loading card art {card_id}: {e}")
            return None

    def _create_white_flash_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Creates a pure white silhouette preserving alpha transparency."""
        flash = surface.copy()
        flash.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        # Re-apply alpha channel from original surface
        alpha_channel = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha_channel.blit(surface, (0, 0))
        # Zero out RGB on mask and keep alpha
        pixels = pygame.PixelArray(alpha_channel)
        # Create solid white with the mask's alpha
        flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, 240))
        flash_surf.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # Fallback to simple additive blend
        flash_simple = surface.copy()
        flash_simple.fill((200, 200, 200, 0), special_flags=pygame.BLEND_RGB_ADD)
        return flash_simple

    def get_hero_sprite(self, char_id: str, target_h: int = 185) -> Optional[tuple[pygame.Surface, pygame.Surface]]:
        cache_key = f"hero_{char_id}_{target_h}"
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key], self._flash_cache[cache_key]

        path = os.path.join(CHAR_SPRITES_DIR, f"{char_id}.png")
        if not os.path.exists(path):
            return None

        try:
            raw = self._load_image(path)
            orig_w, orig_h = raw.get_size()
            scale = target_h / orig_h
            target_w = max(1, int(orig_w * scale))
            scaled = pygame.transform.smoothscale(raw, (target_w, target_h))
            flash = self._create_white_flash_surface(scaled)

            self._sprite_cache[cache_key] = scaled
            self._flash_cache[cache_key] = flash
            return scaled, flash
        except Exception as e:
            print(f"[SpriteManager] Error loading hero sprite {char_id}: {e}")
            return None

    def get_enemy_sprite(self, enemy, target_h: int = 175) -> Optional[tuple[pygame.Surface, pygame.Surface]]:
        cls_name = enemy.__class__.__name__
        enemy_name = getattr(enemy, 'name', '')
        sprite_key = ENEMY_SPRITE_MAP.get(cls_name) or ENEMY_SPRITE_MAP.get(enemy_name)
        if not sprite_key:
            # Fallback by enemy type
            etype = getattr(enemy, 'enemy_type', None)
            if str(etype) == "EnemyType.UNDEAD":
                sprite_key = "skeleton_sentinel"
            elif str(etype) == "EnemyType.BEAST":
                sprite_key = "dread_spider"
            elif str(etype) == "EnemyType.DEMON":
                sprite_key = "void_reaver"
            elif str(etype) == "EnemyType.BOSS":
                sprite_key = "necrolord_malakor"
            else:
                sprite_key = "cultist"

        # Bosses scale larger
        if getattr(enemy, 'is_boss', False):
            target_h = int(target_h * 1.35)
        elif getattr(enemy, 'is_elite', False):
            target_h = int(target_h * 1.15)

        cache_key = f"enemy_{sprite_key}_{target_h}"
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key], self._flash_cache[cache_key]

        path = os.path.join(ENEMY_SPRITES_DIR, f"{sprite_key}.png")
        if not os.path.exists(path):
            return None

        try:
            raw = self._load_image(path)
            orig_w, orig_h = raw.get_size()
            scale = target_h / orig_h
            target_w = max(1, int(orig_w * scale))
            scaled = pygame.transform.smoothscale(raw, (target_w, target_h))

            # Enemies face LEFT (towards the player on the left)
            # The original art faces forward or slightly right/left.
            # In Slay the Spire, enemies on the right face left.
            flipped = pygame.transform.flip(scaled, True, False)
            flash = self._create_white_flash_surface(flipped)

            self._sprite_cache[cache_key] = flipped
            self._flash_cache[cache_key] = flash
            return flipped, flash
        except Exception as e:
            print(f"[SpriteManager] Error loading enemy sprite {sprite_key}: {e}")
            return None

    def get_enemy_head_y(self, enemy, y: int, height: int) -> int:
        """Returns the top Y coordinate of the enemy's visual sprite."""
        res = self.get_enemy_sprite(enemy, target_h=height + 25)
        if res:
            sprite, _ = res
            return (y + height) - sprite.get_height()
        return y

    def _get_drop_shadow(self, width: int, height: int = 24) -> pygame.Surface:
        key = (width, height)
        if key in self._shadow_cache:
            return self._shadow_cache[key]
        surf = pygame.Surface((width + 20, height + 10), pygame.SRCALPHA)
        rect = pygame.Rect(10, 5, width, height)
        # Radial gradient approximation with concentric ellipses
        for i, alpha in enumerate([40, 75, 110, 140]):
            inset = (3 - i) * 2
            r = rect.inflate(-inset * 2, -inset)
            pygame.draw.ellipse(surf, (10, 8, 14, alpha), r)
        self._shadow_cache[key] = surf
        return surf

    def draw_player_sprite(self, surface: pygame.Surface, player, x: int, y: int, width: int, height: int) -> bool:
        res = self.get_hero_sprite(player.char_id, target_h=height + 25)
        if not res:
            return False

        sprite, flash = res
        sw, sh = sprite.get_size()

        # Smooth, calm respiratory breathing curve with ease-in-out easing
        t = self._time * 1.6
        breath = (math.sin(t) + 1.0) * 0.5
        smooth_breath = breath * breath * (3.0 - 2.0 * breath)
        bob_y = -smooth_breath * 3.5

        # Ground anchor (bottom-center aligned)
        ground_x = x + width // 2
        ground_y = y + height

        # Draw drop shadow beneath feet
        shadow = self._get_drop_shadow(width=int(sw * 0.75), height=22)
        surface.blit(shadow, shadow.get_rect(center=(ground_x, ground_y - 2)))

        # Draw character sprite (crisp native scaling without texture shimmer)
        active_sprite = flash if player.flash_timer > 0 else sprite
        sprite_rect = active_sprite.get_rect(midbottom=(ground_x, int(ground_y + bob_y)))
        surface.blit(active_sprite, sprite_rect)
        return True

    def draw_enemy_sprite(self, surface: pygame.Surface, enemy, x: int, y: int, width: int, height: int) -> bool:
        res = self.get_enemy_sprite(enemy, target_h=height + 25)
        if not res:
            return False

        sprite, flash = res
        sw, sh = sprite.get_size()

        # Phase offset based on x position so multiple enemies don't breathe in lockstep
        phase = (x % 500) / 100.0
        t = self._time * 1.6 + phase
        breath = (math.sin(t) + 1.0) * 0.5
        smooth_breath = breath * breath * (3.0 - 2.0 * breath)
        bob_y = -smooth_breath * 3.0

        ground_x = x + width // 2
        ground_y = y + height

        # Drop shadow
        shadow = self._get_drop_shadow(width=int(sw * 0.8), height=24)
        surface.blit(shadow, shadow.get_rect(center=(ground_x, ground_y - 2)))

        # Draw enemy sprite
        active_sprite = flash if enemy.flash_timer > 0 else sprite
        sprite_rect = active_sprite.get_rect(midbottom=(ground_x, int(ground_y + bob_y)))
        surface.blit(active_sprite, sprite_rect)
        return True
