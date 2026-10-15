"""
Card Renderer: Renders styled fantasy cards with rarity frames, costs, types, and descriptions.
"""
import pygame
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
    Renders an ornate dark fantasy trading card.
    """
    w = int(CARD_WIDTH * custom_scale)
    h = int(CARD_HEIGHT * custom_scale)
    card_rect = pygame.Rect(x, y, w, h)

    # Card Type Banner Color
    if card.card_type == CardType.ATTACK:
        type_color = COLOR_ATTACK
    elif card.card_type == CardType.SKILL:
        type_color = COLOR_SKILL
    elif card.card_type == CardType.POWER:
        type_color = COLOR_POWER
    else:
        type_color = COLOR_CURSE

    # Border selection
    if is_hovered:
        border_color = COLOR_CARD_BORDER_HOVER
        border_width = 3
    elif is_playable:
        border_color = COLOR_CARD_BORDER_PLAYABLE
        border_width = 2
    else:
        border_color = COLOR_CARD_BORDER
        border_width = 1

    # Base Card Background
    pygame.draw.rect(surface, COLOR_BG_CARD, card_rect, border_radius=10)

    # Header / Type banner
    header_rect = pygame.Rect(x, y, w, int(30 * custom_scale))
    pygame.draw.rect(surface, type_color, header_rect, border_top_left_radius=10, border_top_right_radius=10)

    # Outer Border
    pygame.draw.rect(surface, border_color, card_rect, width=border_width, border_radius=10)

    # Energy Cost Orb (Top Left)
    effective_cost = card.cost if cost_override is None else cost_override
    orb_radius = int(14 * custom_scale)
    orb_center = (x + orb_radius + 4, y + orb_radius + 4)
    orb_color = (40, 195, 140) if effective_cost == 0 else COLOR_ENERGY_ORB
    pygame.draw.circle(surface, orb_color, orb_center, orb_radius)
    pygame.draw.circle(surface, (255, 230, 200), orb_center, orb_radius, 1)

    cost_str = str(effective_cost)
    cost_txt = FONTS['bold'].render(cost_str, True, (255, 255, 255))
    surface.blit(cost_txt, cost_txt.get_rect(center=orb_center))

    # Card Name
    name_font = FONTS['small'] if len(card.name) > 11 else FONTS['bold']
    name_color = (255, 235, 150) if card.upgraded else COLOR_TEXT_LIGHT
    name_surf = name_font.render(card.name, True, name_color)
    name_rect = name_surf.get_rect(midleft=(x + orb_radius * 2 + 8, y + int(15 * custom_scale)))
    surface.blit(name_surf, name_rect)

    # Illustration Window
    art_rect = pygame.Rect(x + 10, y + int(36 * custom_scale), w - 20, int(65 * custom_scale))
    pygame.draw.rect(surface, (20, 16, 26), art_rect, border_radius=4)
    pygame.draw.rect(surface, (70, 55, 80), art_rect, width=1, border_radius=4)

    # Simple atmospheric art emblem in the art window
    center_art = art_rect.center
    if card.card_type == CardType.ATTACK:
        # Cross swords
        pygame.draw.line(surface, type_color, (center_art[0] - 18, center_art[1] - 18), (center_art[0] + 18, center_art[1] + 18), 3)
        pygame.draw.line(surface, type_color, (center_art[0] + 18, center_art[1] - 18), (center_art[0] - 18, center_art[1] + 18), 3)
    elif card.card_type == CardType.SKILL:
        # Shield emblem
        pygame.draw.polygon(surface, type_color, [
            (center_art[0], center_art[1] - 16),
            (center_art[0] + 16, center_art[1] - 6),
            (center_art[0], center_art[1] + 18),
            (center_art[0] - 16, center_art[1] - 6)
        ])
    elif card.card_type == CardType.POWER:
        # Mystic rune
        pygame.draw.circle(surface, type_color, center_art, 16, 2)
        pygame.draw.circle(surface, (220, 180, 255), center_art, 8)
    else:
        # Skull emblem
        pygame.draw.circle(surface, (120, 50, 120), center_art, 14)

    # Card Type Tag
    type_tag = FONTS['small'].render(card.card_type.value.upper(), True, COLOR_TEXT_MUTED)
    surface.blit(type_tag, type_tag.get_rect(center=(x + w // 2, y + int(112 * custom_scale))))

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

    line_y = y + int(128 * custom_scale)
    for line in desc_lines:
        line_surf = FONTS['small'].render(line, True, COLOR_TEXT_LIGHT)
        surface.blit(line_surf, line_surf.get_rect(center=(x + w // 2, line_y)))
        line_y += 16

    return card_rect
