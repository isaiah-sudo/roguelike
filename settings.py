"""
Game settings and configuration constants for Crypt of the Necrolord.
"""
import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "CRYPT OF THE NECROLORD - Dark Fantasy Roguelike"
GAME_VERSION = "1.4.0"
GITHUB_REPO = "isaiah-sudo/rougelike"

# Color Palette (Dark Gothic Fantasy)
COLOR_BG_DARK = (15, 12, 19)
COLOR_BG_PANEL = (25, 20, 32)
COLOR_BG_CARD = (38, 30, 48)
COLOR_CARD_BORDER = (85, 70, 105)
COLOR_CARD_BORDER_HOVER = (220, 190, 100)
COLOR_CARD_BORDER_PLAYABLE = (70, 200, 140)

# Accent Colors
COLOR_TEXT_LIGHT = (235, 230, 240)
COLOR_TEXT_MUTED = (160, 150, 175)
COLOR_TEXT_GOLD = (255, 215, 80)
COLOR_HEALTH_RED = (210, 45, 60)
COLOR_HEALTH_BG = (60, 20, 25)
COLOR_BLOCK_BLUE = (60, 140, 240)
COLOR_BLOCK_BG = (20, 40, 70)
COLOR_ENERGY_ORB = (220, 70, 40)
COLOR_ENERGY_TEXT = (255, 240, 220)
COLOR_INTENT_ATTACK = (235, 65, 65)
COLOR_INTENT_DEFEND = (70, 150, 245)
COLOR_INTENT_BUFF = (225, 180, 50)
COLOR_INTENT_DEBUFF = (175, 75, 230)

# Card Archetype Theme Colors
COLOR_ATTACK = (180, 50, 50)
COLOR_SKILL = (45, 110, 185)
COLOR_POWER = (130, 60, 190)
COLOR_CURSE = (80, 50, 80)

# Fonts helper
class FontDict(dict):
    def __getitem__(self, key):
        if key not in self:
            init_fonts()
        return super().__getitem__(key)

FONTS = FontDict()

def init_fonts():
    """Initialize system or default fonts for clean UI rendering."""
    if not pygame.font.get_init():
        pygame.font.init()
    FONTS['tiny'] = pygame.font.SysFont("georgia,times,arial", 12)
    FONTS['small'] = pygame.font.SysFont("georgia,times,arial", 14)
    FONTS['regular'] = pygame.font.SysFont("georgia,times,arial", 18)
    FONTS['bold'] = pygame.font.SysFont("georgia,times,arial", 18, bold=True)
    FONTS['medium'] = pygame.font.SysFont("georgia,times,arial", 22, bold=True)
    FONTS['title'] = pygame.font.SysFont("georgia,times,arial", 30, bold=True)
    FONTS['huge'] = pygame.font.SysFont("georgia,times,arial", 46, bold=True)
    FONTS['damage'] = pygame.font.SysFont("impact,arial black,sans-serif", 32)
    FONTS['intent'] = pygame.font.SysFont("georgia,arial", 15, bold=True)

