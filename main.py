"""
Crypt of the Necrolord - Dark Fantasy Deckbuilding Roguelike.
Main entry point and game coordinator.
"""
import sys
import random
import pygame

# Initialize pygame and mixer early
pygame.init()
pygame.mixer.init()

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, init_fonts
init_fonts()

from models.player import Player
from models.enemy import (
    CryptCultist, SkeletonSentinel, PlagueRat, DreadSpider, BloodBat,
    VoidReaver, CinderDemon, MadAlchemist, CorruptedHierophant,
    TormentedWight, NecrolordMalakor, VoidBehemoth,
    InfernalHound, ObsidianGolem, DarkWarlock, FlameArchon, CenturionAutomaton,
    IgnisTheInfernal, ArchmageValerius,
    VoidRevenant, NemesisAvatar, TheCorruptedHeart
)
from systems.map_generator import DungeonMap, NodeType
from systems.combat import CombatState
from systems.reward import CombatReward
from systems.shop import Shop
from systems.events import generate_random_event
from engine.particles import ParticleManager
from engine.visual_fx import ScreenShake
from engine.sound import play_sfx
from views.char_select_view import CharSelectView
from views.combat_view import CombatView
from views.map_view import MapView
from views.reward_view import RewardView
from views.rest_view import RestView
from views.shop_view import ShopView
from views.event_view import EventView
from views.deck_view import DeckView
from views.game_over_view import GameOverView

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.particle_mgr = ParticleManager()
        self.screen_shake = ScreenShake()

        # Start with Character Selection
        self.show_char_select()

    def show_char_select(self):
        self.state = "CHAR_SELECT"
        self.char_select_view = CharSelectView()
        self.current_view = self.char_select_view
        self.deck_overlay = None

    def start_run(self, char_id: str):
        """Initializes a brand new run with the chosen character class."""
        self.player = Player(char_id=char_id)
        self.current_act = 1
        self.dungeon_map = DungeonMap(num_floors=10, paths_per_floor=3, act=self.current_act)
        self.map_view = MapView(self.dungeon_map, self.player)

        self.state = "MAP"
        self.current_view = self.map_view
        self.deck_overlay = None

        self.combat_state = None
        self.combat_view = None
        self.is_current_elite = False
        self.is_current_boss = False

    def ascend_to_next_act(self):
        """Ascend to the next Act after claiming boss loot, generating a new floor map with tougher foes."""
        self.current_act += 1
        # Heal 75% max HP upon ascending
        heal_amount = int(self.player.max_hp * 0.75)
        self.player.heal(heal_amount)
        play_sfx('victory', 0.8)

        # Generate fresh Dungeon Map for the new Act
        self.dungeon_map = DungeonMap(num_floors=10, paths_per_floor=3, act=self.current_act)
        self.map_view = MapView(self.dungeon_map, self.player)
        self.state = "MAP"
        self.current_view = self.map_view

    def enter_node(self, node):
        ntype = node.node_type
        if ntype == NodeType.MONSTER:
            self._start_combat(is_elite=False, is_boss=False)
        elif ntype == NodeType.ELITE:
            self._start_combat(is_elite=True, is_boss=False)
        elif ntype == NodeType.BOSS:
            self._start_combat(is_elite=False, is_boss=True)
        elif ntype == NodeType.REST:
            self.state = "REST"
            self.current_view = RestView(self.player)
        elif ntype == NodeType.SHOP:
            self.state = "SHOP"
            self.current_view = ShopView(Shop(), self.player)
        elif ntype == NodeType.EVENT:
            self.state = "EVENT"
            event = generate_random_event(self.player)
            self.current_view = EventView(event, self.player)

    def _start_combat(self, is_elite: bool = False, is_boss: bool = False):
        self.is_current_elite = is_elite
        self.is_current_boss = is_boss

        if is_boss:
            if self.current_act == 1:
                boss_pools = [
                    [NecrolordMalakor()],
                    [VoidBehemoth()]
                ]
            elif self.current_act == 2:
                boss_pools = [
                    [IgnisTheInfernal()],
                    [ArchmageValerius()]
                ]
            else:
                boss_pools = [
                    [TheCorruptedHeart()],
                    [IgnisTheInfernal()],
                    [NecrolordMalakor()]
                ]
            enemies = random.choice(boss_pools)
        elif is_elite:
            if self.current_act == 1:
                elite_pools = [
                    [TormentedWight()],
                    [VoidReaver()],
                    [CinderDemon(), MadAlchemist()]
                ]
            elif self.current_act == 2:
                elite_pools = [
                    [FlameArchon()],
                    [CenturionAutomaton()],
                    [FlameArchon(), DarkWarlock()]
                ]
            else:
                elite_pools = [
                    [NemesisAvatar()],
                    [CenturionAutomaton(), NemesisAvatar()],
                    [FlameArchon(), CenturionAutomaton()]
                ]
            enemies = random.choice(elite_pools)
        else:
            if self.current_act == 1:
                normal_pools = [
                    [CryptCultist()],
                    [SkeletonSentinel()],
                    [PlagueRat(), PlagueRat()],
                    [BloodBat(), BloodBat()],
                    [BloodBat(), PlagueRat()],
                    [DreadSpider()],
                    [CinderDemon()],
                    [MadAlchemist()],
                    [CorruptedHierophant(), SkeletonSentinel()],
                    [CryptCultist(), DreadSpider()]
                ]
            elif self.current_act == 2:
                normal_pools = [
                    [InfernalHound(), InfernalHound()],
                    [ObsidianGolem()],
                    [DarkWarlock(), InfernalHound()],
                    [CinderDemon(), DarkWarlock()],
                    [SkeletonSentinel(), ObsidianGolem()],
                    [InfernalHound(), DreadSpider()]
                ]
            else:
                normal_pools = [
                    [VoidRevenant()],
                    [VoidRevenant(), InfernalHound()],
                    [ObsidianGolem(), VoidRevenant()],
                    [DarkWarlock(), VoidRevenant()],
                    [InfernalHound(), InfernalHound(), InfernalHound()]
                ]
            enemies = random.choice(normal_pools)

        # Scale monster stats for higher Acts / Ascension
        if self.current_act > 1:
            scale_factor = 1.0 + (self.current_act - 1) * 0.18
            for e in enemies:
                e.max_hp = int(e.max_hp * scale_factor)
                e.hp = e.max_hp
                if self.current_act >= 3:
                    e.statuses.apply("Strength", self.current_act - 2)

        self.combat_state = CombatState(self.player, enemies, self.particle_mgr, self.screen_shake)
        self.combat_view = CombatView(self.combat_state)
        self.state = "COMBAT"
        self.current_view = self.combat_view

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                # Global Deck view toggle
                if self.deck_overlay is not None:
                    action = self.deck_overlay.handle_event(event, mouse_pos)
                    if action == "close_deck":
                        self.deck_overlay = None
                    continue

                if event.type == pygame.KEYDOWN and event.key == pygame.K_d and self.state in ("MAP", "COMBAT"):
                    self.deck_overlay = DeckView(self.player)
                    continue

                # Character Select State
                if self.state == "CHAR_SELECT":
                    action, char_id = self.current_view.handle_event(event, mouse_pos)
                    if action == "start_game" and char_id:
                        self.start_run(char_id)

                # View-specific event handling
                elif self.state == "MAP":
                    action, node = self.current_view.handle_event(event, mouse_pos)
                    if action == "enter_node" and node:
                        self.enter_node(node)
                    elif action == "open_deck":
                        self.deck_overlay = DeckView(self.player)

                elif self.state == "COMBAT":
                    action = self.current_view.handle_event(event, mouse_pos)
                    if action == "victory":
                        self.state = "REWARD"
                        reward = CombatReward(is_elite=self.is_current_elite, is_boss=self.is_current_boss, act=self.current_act)
                        self.current_view = RewardView(reward, self.player)
                    elif action == "defeat":
                        cumul_floor = self.dungeon_map.get_cumulative_floor() if hasattr(self.dungeon_map, 'get_cumulative_floor') else self.dungeon_map.current_floor + 1
                        self.state = "GAME_OVER"
                        self.current_view = GameOverView(False, self.player, cumul_floor)

                elif self.state in ("REWARD", "REST", "SHOP", "EVENT"):
                    action = self.current_view.handle_event(event, mouse_pos)
                    if action == "ascend_act":
                        self.ascend_to_next_act()
                    elif action == "back_to_map":
                        self.state = "MAP"
                        self.current_view = self.map_view

                elif self.state == "GAME_OVER":
                    action = self.current_view.handle_event(event, mouse_pos)
                    if action == "restart":
                        self.show_char_select()

            # Update Logic
            if self.deck_overlay is not None:
                self.deck_overlay.update(dt, mouse_pos)
            else:
                self.current_view.update(dt, mouse_pos)

            # Drawing
            self.current_view.draw(self.screen)
            if self.deck_overlay is not None:
                self.deck_overlay.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
