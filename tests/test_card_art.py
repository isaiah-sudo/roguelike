import unittest
import pygame
import inspect
import os
import models.card as mc
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.sprite_manager import SpriteManager

class TestCardArt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Initialize a headless display surface so convert_alpha() / smoothscale work
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_all_cards_have_art_assets(self):
        card_classes = [c for name, c in inspect.getmembers(mc, inspect.isclass) if issubclass(c, mc.Card) and c is not mc.Card]
        card_instances = [c() for c in card_classes]
        unique_ids = {c.id_name for c in card_instances}

        sm = SpriteManager.get()
        missing = []
        for cid in sorted(unique_ids):
            art = sm.get_card_art(cid, (130, 64))
            if art is None:
                missing.append(cid)

        self.assertEqual(missing, [], f"Missing card art for: {missing}")

    def test_draw_card_renders_with_art(self):
        surface = pygame.Surface((300, 400), pygame.SRCALPHA)
        strike = mc.StrikeCard()
        rect = draw_card(surface, strike, 20, 20, is_hovered=True, is_playable=True)
        self.assertEqual(rect.width, CARD_WIDTH)
        self.assertEqual(rect.height, CARD_HEIGHT)

    def test_draw_card_upgraded_and_scaled(self):
        surface = pygame.Surface((400, 500), pygame.SRCALPHA)
        strike = mc.StrikeCard()
        strike.upgrade()
        rect = draw_card(surface, strike, 30, 30, is_hovered=False, is_playable=True, custom_scale=1.2)
        self.assertEqual(rect.width, int(CARD_WIDTH * 1.2))
        self.assertEqual(rect.height, int(CARD_HEIGHT * 1.2))

if __name__ == "__main__":
    unittest.main()
