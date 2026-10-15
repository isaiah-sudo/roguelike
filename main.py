"""
Crypt of the Necrolord - Dark Fantasy Deckbuilding Roguelike.
Main entry point and game coordinator.
"""
import os
import sys
import random
import pygame

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

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
from views.title_view import TitleView
from views.load_game_view import LoadGameView
from views.char_select_view import CharSelectView
from views.combat_view import CombatView
from views.map_view import MapView
from views.reward_view import RewardView
from views.rest_view import RestView
from views.shop_view import ShopView
from views.event_view import EventView
from views.deck_view import DeckView
from views.game_over_view import GameOverView
from systems.save_manager import (
    save_game, load_game, delete_save, get_first_empty_slot, get_latest_save_slot, has_any_save
)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        # Set game window icon
        icon_path = resource_path(os.path.join("assets", "icon.png"))
        if os.path.exists(icon_path):
            try:
                icon_surface = pygame.image.load(icon_path)
                pygame.display.set_icon(icon_surface)
            except Exception as e:
                print(f"[Game] Warning: Could not set window icon: {e}")

        self.clock = pygame.time.Clock()
        self.running = True

        self.particle_mgr = ParticleManager()
        self.screen_shake = ScreenShake()

        self.current_slot = 1
        self.player = None
        self.dungeon_map = None
        self.current_act = 1
        self.is_current_elite = False
        self.is_current_boss = False
        self.deck_overlay = None

        # Start on Title Screen
        self.show_title_screen()

    def show_title_screen(self):
        self.state = "TITLE"
        self.title_view = TitleView()
        self.current_view = self.title_view
        self.deck_overlay = None

    def show_load_game(self):
        self.state = "LOAD_GAME"
        self.load_game_view = LoadGameView()
        self.current_view = self.load_game_view
        self.deck_overlay = None

    def show_char_select(self, target_slot: int = None):
        if target_slot is None:
            target_slot = get_first_empty_slot()
        self.current_slot = target_slot
        self.state = "CHAR_SELECT"
        self.char_select_view = CharSelectView(target_slot=self.current_slot)
        self.current_view = self.char_select_view
        self.deck_overlay = None

    def start_run(self, char_id: str, slot_id: int = None):
        """Initializes a brand new run with the chosen character class and auto-saves."""
        if slot_id is not None:
            self.current_slot = slot_id
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

        # Persist new run
        self.save_current_run()

    def load_run(self, slot_id: int):
        """Loads an existing run from a save slot and resumes on the dungeon map."""
        data = load_game(slot_id)
        if not data:
            self.show_title_screen()
            return

        self.current_slot = slot_id
        self.player = data["player"]
        self.dungeon_map = data["dungeon_map"]
        self.current_act = data["current_act"]
        self.is_current_elite = data["is_current_elite"]
        self.is_current_boss = data["is_current_boss"]

        self.combat_state = None
        self.combat_view = None
        self.deck_overlay = None

        self.map_view = MapView(self.dungeon_map, self.player)
        self.state = "MAP"
        self.current_view = self.map_view

    def save_current_run(self):
        """Saves current active run to disk."""
        if getattr(self, 'player', None) is not None and getattr(self, 'dungeon_map', None) is not None:
            save_game(
                self.current_slot,
                self.player,
                self.dungeon_map,
                self.current_act,
                self.is_current_elite,
                self.is_current_boss
            )

    def ascend_to_next_act(self):
        """Ascend to the next Act after claiming boss loot, generating a new floor map with tougher foes."""
        self.current_act += 1
        # Heal 40% max HP upon ascending
        heal_amount = int(self.player.max_hp * 0.40)
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

        # Scale monster stats dynamically for depth, Acts, Elites, and Bosses
        current_floor = getattr(self.dungeon_map, 'current_floor', 0)
        hp_mult = 1.0
        bonus_str = 0

        if self.current_act == 1:
            if current_floor >= 4:
                hp_mult += 0.10
                bonus_str += 1
            if current_floor >= 7:
                hp_mult += 0.12
        elif self.current_act == 2:
            hp_mult += 0.30
            bonus_str += 2
            if current_floor >= 5:
                hp_mult += 0.15
                bonus_str += 1
        elif self.current_act >= 3:
            hp_mult += 0.55
            bonus_str += 4
            if current_floor >= 5:
                hp_mult += 0.20
                bonus_str += 1

        if is_elite:
            hp_mult += 0.15
            bonus_str += 1
        elif is_boss:
            hp_mult += 0.25
            bonus_str += 1

        for e in enemies:
            e.max_hp = int(e.max_hp * hp_mult)
            e.hp = e.max_hp
            if bonus_str > 0:
                e.statuses.apply("Strength", bonus_str)

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
                    if self.state in ("MAP", "REST", "SHOP", "EVENT", "REWARD") and getattr(self, 'player', None):
                        self.save_current_run()
                    self.running = False
                    break

                # Global Deck view toggle
                if self.deck_overlay is not None:
                    action = self.deck_overlay.handle_event(event, mouse_pos)
                    if action == "close_deck":
                        self.deck_overlay = None
                    continue

                if event.type == pygame.KEYDOWN and event.key == pygame.K_d and self.state in ("MAP", "COMBAT", "REST", "SHOP", "EVENT", "REWARD") and getattr(self, 'player', None):
                    self.deck_overlay = DeckView(self.player)
                    continue

                # Title Screen State
                if self.state == "TITLE":
                    action, data = self.current_view.handle_event(event, mouse_pos)
                    if action == "continue" and data:
                        self.load_run(data)
                    elif action == "new_run":
                        self.show_char_select()
                    elif action == "load_game":
                        self.show_load_game()
                    elif action == "quit":
                        self.running = False
                        break

                # Load Game / Slot Selection State
                elif self.state == "LOAD_GAME":
                    action, data = self.current_view.handle_event(event, mouse_pos)
                    if action == "load_slot" and data:
                        self.load_run(data)
                    elif action == "new_run_slot" and data:
                        self.show_char_select(target_slot=data)
                    elif action == "back_to_title":
                        self.show_title_screen()

                # Character Select State
                elif self.state == "CHAR_SELECT":
                    action, data = self.current_view.handle_event(event, mouse_pos)
                    if action == "start_game" and data:
                        self.start_run(data, self.current_slot)
                    elif action == "back_to_title":
                        self.show_title_screen()

                # View-specific event handling
                elif self.state == "MAP":
                    action, node = self.current_view.handle_event(event, mouse_pos)
                    if action == "enter_node" and node:
                        self.enter_node(node)
                        self.save_current_run()
                    elif action == "open_deck":
                        self.deck_overlay = DeckView(self.player)
                    elif action == "save_and_quit":
                        self.save_current_run()
                        self.show_title_screen()

                elif self.state == "COMBAT":
                    action = self.current_view.handle_event(event, mouse_pos)
                    if action == "victory":
                        self.state = "REWARD"
                        reward = CombatReward(is_elite=self.is_current_elite, is_boss=self.is_current_boss, act=self.current_act)
                        self.current_view = RewardView(reward, self.player)
                        self.save_current_run()
                    elif action == "defeat":
                        delete_save(self.current_slot)
                        cumul_floor = self.dungeon_map.get_cumulative_floor() if hasattr(self.dungeon_map, 'get_cumulative_floor') else self.dungeon_map.current_floor + 1
                        self.state = "GAME_OVER"
                        self.current_view = GameOverView(False, self.player, cumul_floor)

                elif self.state in ("REWARD", "REST", "SHOP", "EVENT"):
                    action = self.current_view.handle_event(event, mouse_pos)
                    if action == "ascend_act":
                        self.ascend_to_next_act()
                        self.save_current_run()
                    elif action == "back_to_map":
                        self.state = "MAP"
                        self.current_view = self.map_view
                        self.save_current_run()

                elif self.state == "GAME_OVER":
                    action = self.current_view.handle_event(event, mouse_pos)
                    if action == "restart":
                        self.show_char_select()
                    elif action == "title_menu":
                        self.show_title_screen()

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
