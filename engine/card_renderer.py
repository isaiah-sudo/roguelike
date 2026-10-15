"""
Card Renderer: Renders ornate dark fantasy cards with rarity gems, glowing frames,
foil sheens, upgraded golden trim, and clear combat cost indicators.
"""
import pygame
import math
from models.card import Card, CardType, CardRarity
from settings import (
    COLOR_BG_CARD, COLOR_CARD_BORDER, COLOR_CARD_BORDER_HOVER, COLOR_CARD_BORDER_PLAYABLE,
    COLOR_ATTACK, COLOR_SKILL, COLOR_POWER, COLOR_CURSE,
    COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED, COLOR_ENERGY_ORB, FONTS
)

CARD_WIDTH = 150
CARD_HEIGHT = 210

def draw_card(surface, card: Card, x: int, y: int, is_hovered: bool = False, is_playable: bool = True, custom_scale: float = 1.0, cost_override: int = None):
    """
    Renders an ornate dark fantasy trading card with animated hover effects and upgraded trim.
    """
    w = int(CARD_WIDTH * custom_scale)
    h = int(CARD_HEIGHT * custom_scale)
    card_rect = pygame.Rect(x, y, w, h)

    # 1. Card Type Banner Color
    if card.card_type == CardType.ATTACK:
        type_color = COLOR_ATTACK
        accent_color = (255, 110, 110)
    elif card.card_type == CardType.SKILL:
        type_color = COLOR_SKILL
        accent_color = (110, 190, 255)
    elif card.card_type == CardType.POWER:
        type_color = COLOR_POWER
        accent_color = (220, 140, 255)
    else:
        type_color = COLOR_CURSE
        accent_color = (180, 80, 180)

    # 2. Border selection & Outer Glow on Hover
    if is_hovered:
        border_color = (255, 230, 120) if card.upgraded else COLOR_CARD_BORDER_HOVER
        border_width = 3
        # Outer soft glow halo
        glow_size = int(12 * custom_scale)
        glow_surf = pygame.Surface((w + glow_size * 2, h + glow_size * 2), pygame.SRCALPHA)
        glow_alpha = 60 if not card.upgraded else 85
        glow_col = (*border_color[:3], glow_alpha)
        pygame.draw.rect(glow_surf, glow_col, (0, 0, w + glow_size * 2, h + glow_size * 2), border_radius=14)
        surface.blit(glow_surf, (x - glow_size, y - glow_size))
    elif card.upgraded:
        border_color = (215, 175, 75)
        border_width = 2
    elif is_playable:
        border_color = COLOR_CARD_BORDER_PLAYABLE
        border_width = 2
    else:
        border_color = COLOR_CARD_BORDER
        border_width = 1

    # Base Card Background with subtle gradient feel
    pygame.draw.rect(surface, COLOR_BG_CARD, card_rect, border_radius=10)

    # Header / Type banner
    header_h = int(32 * custom_scale)
    header_rect = pygame.Rect(x, y, w, header_h)
    pygame.draw.rect(surface, type_color, header_rect, border_top_left_radius=10, border_top_right_radius=10)

    # Inner banner shade line
    pygame.draw.line(surface, (20, 16, 26), (x, y + header_h), (x + w, y + header_h), 2)

    # Outer Border
    pygame.draw.rect(surface, border_color, card_rect, width=border_width, border_radius=10)

    # Upgraded Ornate Corner Accents
    if card.upgraded:
        corner_sz = int(10 * custom_scale)
        # Top-right corner tag
        pygame.draw.polygon(surface, (255, 220, 80), [
            (x + w - corner_sz * 2, y),
            (x + w, y),
            (x + w, y + corner_sz * 2)
        ])
        plus_txt = FONTS['small'].render("+", True, (30, 20, 10))
        surface.blit(plus_txt, (x + w - 12, y + 1))

    # Energy Cost Orb (Top Left)
    effective_cost = card.cost if cost_override is None else cost_override
    orb_radius = int(14 * custom_scale)
    orb_center = (x + orb_radius + 4, y + orb_radius + 4)
    orb_color = (35, 180, 130) if effective_cost == 0 else COLOR_ENERGY_ORB

    # Orb 3D bevel shading
    pygame.draw.circle(surface, (15, 12, 20), (orb_center[0] + 1, orb_center[1] + 1), orb_radius + 1)
    pygame.draw.circle(surface, orb_color, orb_center, orb_radius)
    # Highlight arc
    pygame.draw.circle(surface, (255, 255, 255), (orb_center[0] - 4, orb_center[1] - 4), int(orb_radius * 0.45))
    pygame.draw.circle(surface, orb_color, (orb_center[0] - 3, orb_center[1] - 3), int(orb_radius * 0.40))
    pygame.draw.circle(surface, (255, 220, 180), orb_center, orb_radius, 1)

    cost_str = str(effective_cost)
    cost_txt = FONTS['bold'].render(cost_str, True, (255, 255, 255))
    surface.blit(cost_txt, cost_txt.get_rect(center=orb_center))

    # Card Name
    name_font = FONTS['small'] if len(card.name) > 11 else FONTS['bold']
    name_color = (255, 235, 130) if card.upgraded else COLOR_TEXT_LIGHT
    name_surf = name_font.render(card.name, True, name_color)
    name_rect = name_surf.get_rect(midleft=(x + orb_radius * 2 + 8, y + int(16 * custom_scale)))
    surface.blit(name_surf, name_rect)

    # Illustration Window
    art_rect = pygame.Rect(x + 10, y + int(38 * custom_scale), w - 20, int(64 * custom_scale))
    pygame.draw.rect(surface, (18, 14, 24), art_rect, border_radius=6)
    pygame.draw.rect(surface, (65, 50, 75), art_rect, width=1, border_radius=6)

    # Art emblem in the illustration window
    center_art = art_rect.center
    if card.card_type == CardType.ATTACK:
        # Cross swords with hilt and guard
        pygame.draw.line(surface, type_color, (center_art[0] - 18, center_art[1] - 16), (center_art[0] + 18, center_art[1] + 16), 3)
        pygame.draw.line(surface, type_color, (center_art[0] + 18, center_art[1] - 16), (center_art[0] - 18, center_art[1] + 16), 3)
        pygame.draw.line(surface, accent_color, (center_art[0] - 14, center_art[1] - 12), (center_art[0] + 14, center_art[1] + 12), 1)
        # Blade gleam
        pygame.draw.circle(surface, (255, 255, 255), (center_art[0] - 16, center_art[1] - 14), 2)
    elif card.card_type == CardType.SKILL:
        # Heraldic shield emblem with inner cross
        pygame.draw.polygon(surface, type_color, [
            (center_art[0], center_art[1] - 16),
            (center_art[0] + 16, center_art[1] - 7),
            (center_art[0], center_art[1] + 18),
            (center_art[0] - 16, center_art[1] - 7)
        ])
        pygame.draw.polygon(surface, accent_color, [
            (center_art[0], center_art[1] - 13),
            (center_art[0] + 12, center_art[1] - 5),
            (center_art[0], center_art[1] + 14),
            (center_art[0] - 12, center_art[1] - 5)
        ], 1)
        pygame.draw.line(surface, (255, 255, 255), (center_art[0], center_art[1] - 8), (center_art[0], center_art[1] + 10), 2)
    elif card.card_type == CardType.POWER:
        # Mystic occult rune with core star
        pygame.draw.circle(surface, type_color, center_art, 16, 2)
        pygame.draw.circle(surface, accent_color, center_art, 10, 1)
        pygame.draw.circle(surface, (255, 240, 255), center_art, 4)
        pygame.draw.line(surface, (255, 255, 255), (center_art[0] - 8, center_art[1]), (center_art[0] + 8, center_art[1]), 1)
        pygame.draw.line(surface, (255, 255, 255), (center_art[0], center_art[1] - 8), (center_art[0], center_art[1] + 8), 1)
    else:
        # Horned Skull emblem
        pygame.draw.circle(surface, (130, 45, 120), center_art, 14)
        pygame.draw.circle(surface, (20, 10, 20), (center_art[0] - 5, center_art[1] - 2), 3)
        pygame.draw.circle(surface, (20, 10, 20), (center_art[0] + 5, center_art[1] - 2), 3)

    # Rarity Gem underneath art
    rarity = getattr(card, 'rarity', CardRarity.COMMON)
    if rarity == CardRarity.RARE:
        gem_col = (255, 210, 50)
    elif rarity == CardRarity.UNCOMMON:
        gem_col = (70, 160, 255)
    else:
        gem_col = (160, 160, 175)

    gem_x = x + w // 2
    gem_y = art_rect.bottom + 5
    pygame.draw.polygon(surface, gem_col, [
        (gem_x, gem_y - 4), (gem_x + 4, gem_y), (gem_x, gem_y + 4), (gem_x - 4, gem_y)
    ])

    # Card Type Tag
    type_tag = FONTS['small'].render(card.card_type.value.upper(), True, COLOR_TEXT_MUTED)
    surface.blit(type_tag, type_tag.get_rect(center=(x + w // 2, y + int(114 * custom_scale))))

    # Description Text (multi-line word wrapped)
    desc_words = card.description.split(' ')
    desc_lines = []
    curr_line = []
    
    for word in desc_words:
        test_line = ' '.join(curr_line + [word])
        if FONTS['small'].size(test_line)[0] < w - 20:
            curr_line.append(word)
        else:
            if curr_line:
                desc_lines.append(' '.join(curr_line))
            curr_line = [word]
    if curr_line:
        desc_lines.append(' '.join(curr_line))

    line_y = y + int(130 * custom_scale)
    for line in desc_lines:
        line_surf = FONTS['small'].render(line, True, COLOR_TEXT_LIGHT)
        surface.blit(line_surf, line_surf.get_rect(center=(x + w // 2, line_y)))
        line_y += 16

    return card_rect
