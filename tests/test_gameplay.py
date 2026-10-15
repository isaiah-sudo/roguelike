"""
Automated unit, combo, and multi-character simulation tests for Crypt of the Necrolord.
"""
import unittest
import pygame
pygame.init()

from models.player import Player
from models.enemy import (
    CryptCultist, SkeletonSentinel, PlagueRat, DreadSpider,
    VoidReaver, CinderDemon, MadAlchemist, CorruptedHierophant,
    NecrolordMalakor, VoidBehemoth
)
from models.card import (
    StrikeCard, DefendCard, BashCard, HeavyBladeCard,
    DeadlyPoisonCard, CatalystCard, AdrenalineCard, FlexCard,
    SeeingRedCard, WarcryCard, OfferingCard, HemokinesisCard,
    RuptureCard, CombustionCard, BloodForBloodCard, BodySlamCard,
    EntrenchCard, BarricadeCard, FlameBarrierCard, FeelNoPainCard,
    DarkEmbraceCard, CorruptionCard, SecondWindCard, ShivCard,
    BladeDanceCard, AccuracyCard, FinisherCard, DoubleTapCard,
    BurstCard, CorpseExplosionCard, NeutralizeCard, LimitBreakCard,
    WraithFormCard, SoulDrainCard, AngerCard
)
from models.relic import (
    BurningBloodRelic, RingOfTheSerpentRelic, SoulPhylacteryRelic,
    AnchorRelic, VajraRelic
)
from systems.combat import CombatState
from systems.map_generator import DungeonMap, NodeType
from systems.shop import Shop
from engine.particles import ParticleManager
from engine.visual_fx import ScreenShake

class TestRoguelikeGameplay(unittest.TestCase):
    def setUp(self):
        self.particle_mgr = ParticleManager()
        self.screen_shake = ScreenShake()

    def test_playable_characters(self):
        # 1. Blood Knight
        knight = Player(char_id="blood_knight")
        self.assertEqual(knight.hp, 80)
        self.assertEqual(knight.max_hp, 80)
        self.assertEqual(knight.class_title, "Vanguard of Ruin")
        self.assertTrue(knight.has_relic("burning_blood"))
        # Check starter deck has Flex and Bash
        card_names = [c.name for c in knight.deck]
        self.assertIn("Flex", card_names)
        self.assertIn("Bash", card_names)

        # 2. Shadow Assassin
        assassin = Player(char_id="shadow_assassin")
        self.assertEqual(assassin.hp, 70)
        self.assertEqual(assassin.class_title, "Nightshade Weaver")
        self.assertTrue(assassin.has_relic("ring_serpent"))
        assassin_names = [c.name for c in assassin.deck]
        self.assertIn("Neutralize", assassin_names)
        self.assertIn("Blade Dance", assassin_names)
        self.assertIn("Deadly Poison", assassin_names)

        # 3. Void Necromancer
        necro = Player(char_id="void_necromancer")
        self.assertEqual(necro.hp, 68)
        self.assertEqual(necro.class_title, "Scion of the Abyss")
        self.assertTrue(necro.has_relic("soul_phylactery"))
        necro_names = [c.name for c in necro.deck]
        self.assertIn("Soul Drain", necro_names)
        self.assertIn("Dark Offering", necro_names)
        self.assertIn("Corpse Explosion", necro_names)

    def test_intangible_mechanic(self):
        player = Player(char_id="shadow_assassin")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)

        # Play Wraith Form (Gain Intangible)
        wf = WraithFormCard()
        player.hand.append(wf)
        player.energy = 3
        combat.play_card(wf)
        self.assertTrue(player.statuses.get("Intangible") > 0)

        # Cultist hits with 30 raw damage; Intangible reduces damage to 1!
        initial_hp = player.hp
        combat.deal_attack_damage(cultist, player, 30)
        self.assertEqual(player.hp, initial_hp - 1)

    def test_limit_break_and_strength_exponential(self):
        player = Player(char_id="blood_knight")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)

        # Flex (+2 Str) then Limit Break (doubles to +4 Str)
        flex = FlexCard()
        lb = LimitBreakCard()
        player.hand.extend([flex, lb])
        player.energy = 3
        combat.play_card(flex)
        combat.play_card(lb)
        self.assertEqual(player.statuses.get("Strength"), 4)

    def test_soul_drain_lifesteal(self):
        player = Player(char_id="void_necromancer")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)

        player.hp = 50
        sd = SoulDrainCard()
        player.hand.append(sd)
        player.energy = 3
        combat.play_card(sd, cultist)
        self.assertEqual(player.hp, 53)

    def test_burning_blood_relic(self):
        player = Player(char_id="blood_knight")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)

        player.hp = 60
        # End combat with victory
        for relic in player.relics:
            relic.on_combat_end(combat, player, won=True)
        self.assertEqual(player.hp, 66)

    def test_diverse_enemy_behaviors(self):
        # 1. Cinder Demon starts with Thorns
        cinder = CinderDemon()
        self.assertEqual(cinder.statuses.get("Thorns"), 3)

        # 2. Dread Spider multi-hits and inflicts Weak/Vulnerable
        spider = DreadSpider()
        player = Player(char_id="blood_knight")
        combat = CombatState(player, [spider], self.particle_mgr, self.screen_shake)
        spider.decide_intent(combat)
        self.assertEqual(spider.intent.desc, "Web Spit (Weak 2 + Vulnerable 1)")
        spider.execute_turn(combat, player)
        self.assertTrue(player.statuses.has("Weak"))
        self.assertTrue(player.statuses.has("Vulnerable"))

        # 3. Void Reaver has high HP and elite scaling
        reaver = VoidReaver()
        self.assertTrue(reaver.is_elite)
        self.assertEqual(reaver.max_hp, 88)

        # 4. Void Behemoth boss
        behemoth = VoidBehemoth()
        self.assertTrue(behemoth.is_boss)
        self.assertEqual(behemoth.max_hp, 145)

        # 5. Blood Bat leech and screech
        from models.enemy import BloodBat
        bat = BloodBat()
        self.assertEqual(bat.hp, 36)
        bat.decide_intent(combat)
        self.assertEqual(bat.intent.desc, "Vampiric Bite (Heals 3)")

    def test_zero_cost_cards_and_buffs(self):
        player = Player(char_id="blood_knight")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)
        player.energy = 3

        sr = SeeingRedCard()
        player.hand.append(sr)
        combat.play_card(sr)
        self.assertEqual(player.energy, 5)

        adren = AdrenalineCard()
        player.hand.append(adren)
        combat.play_card(adren)
        self.assertEqual(player.energy, 6)

    def test_barricade_entrench_bodyslam_combo(self):
        player = Player(char_id="blood_knight")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)

        barricade = BarricadeCard()
        player.hand.append(barricade)
        player.energy = 5
        combat.play_card(barricade)
        self.assertTrue(player.statuses.has("Barricade"))

        player.gain_block(10)
        entrench = EntrenchCard()
        player.hand.append(entrench)
        combat.play_card(entrench)
        self.assertEqual(player.block, 20)

        combat.end_player_turn()
        combat.resolve_all_enemy_turns()
        self.assertEqual(player.block, 20)

        initial_hp = cultist.hp
        slam = BodySlamCard()
        player.hand.append(slam)
        player.energy = 3
        combat.play_card(slam, cultist)
        self.assertEqual(cultist.hp, initial_hp - 20)

    def test_advanced_slay_the_spire_cards(self):
        player = Player(char_id="blood_knight")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)

        # 1. Armaments: upgrades a card in hand for combat
        from models.card import ArmamentsCard, StrikeCard, FeedCard, FiendFireCard
        arm = ArmamentsCard()
        strike = StrikeCard()
        player.hand = [arm, strike]
        player.energy = 4
        combat.play_card(arm)
        self.assertTrue(strike.upgraded)

        # 2. Feed: fatal kill increases permanent max HP
        cultist.hp = 5
        feed = FeedCard()
        player.hand.append(feed)
        init_max_hp = player.max_hp
        combat.play_card(feed, cultist)
        self.assertEqual(player.max_hp, init_max_hp + 3)

        # 3. Fiend Fire: exhausts hand and strikes for each
        c2 = CryptCultist()
        c2.hp = 40
        combat.enemies = [c2]
        combat.phase = "player_turn"
        ff = FiendFireCard()
        player.hand = [ff, StrikeCard(), StrikeCard(), StrikeCard()]
        player.energy = 3
        combat.play_card(ff, c2)
        # 3 cards exhausted * 7 dmg = 21 dmg
        self.assertEqual(c2.hp, 40 - 21)

    def test_shivs_accuracy_and_finisher_chain(self):
        player = Player(char_id="shadow_assassin")
        cultist = CryptCultist()
        combat = CombatState(player, [cultist], self.particle_mgr, self.screen_shake)

        acc = AccuracyCard()
        player.hand.append(acc)
        player.energy = 4
        combat.play_card(acc)

        shiv1 = ShivCard()
        shiv2 = ShivCard()
        player.hand.extend([shiv1, shiv2])
        init_enemy_hp = cultist.hp
        combat.play_card(shiv1, cultist)
        combat.play_card(shiv2, cultist)
        self.assertEqual(cultist.hp, init_enemy_hp - 16)

        finisher = FinisherCard()
        player.hand.append(finisher)
        prev_hp = cultist.hp
        combat.play_card(finisher, cultist)
        self.assertEqual(cultist.hp, prev_hp - 18)

    def test_corpse_explosion_detonation(self):
        player = Player(char_id="void_necromancer")
        e1 = PlagueRat()
        e2 = CryptCultist()
        combat = CombatState(player, [e1, e2], self.particle_mgr, self.screen_shake)

        ce = CorpseExplosionCard()
        player.hand.append(ce)
        player.energy = 3
        combat.play_card(ce, e1)

        e1.hp = 0
        combat._handle_entity_death(e1)
        self.assertEqual(e2.hp, 50 - 40)

    def test_combat_view_updates_and_banner_lifecycle(self):
        """Verifies CombatView and CombatState update/draw loops run without missing attributes."""
        from views.combat_view import CombatView
        surface = pygame.Surface((1280, 720))
        player = Player(char_id="blood_knight")
        enemy = CryptCultist()
        combat = CombatState(player, [enemy], self.particle_mgr, self.screen_shake)
        view = CombatView(combat)

        # Update several ticks immediately (which caught the previous banner_timer bug)
        for _ in range(10):
            view.update(0.016, (640, 360))
            combat.update(0.016)

        # Draw frame
        view.draw(surface)

        # Trigger enemy turn and update through stages
        combat.end_player_turn()
        self.assertEqual(combat.phase, "enemy_turn")
        self.assertTrue(combat.banner_timer > 0)
        view.update(0.016, (640, 360))
        view.draw(surface)

    def test_all_views_update_and_draw(self):
        """Exercises every single game view's update and draw to verify 100% attribute integrity."""
        from views.char_select_view import CharSelectView
        from views.map_view import MapView
        from views.reward_view import RewardView
        from views.rest_view import RestView
        from views.shop_view import ShopView
        from views.event_view import EventView
        from views.deck_view import DeckView
        from views.game_over_view import GameOverView
        from systems.reward import CombatReward
        from systems.shop import Shop
        from systems.events import generate_random_event

        surface = pygame.Surface((1280, 720))
        player = Player(char_id="shadow_assassin")

        # 1. Char select
        csv = CharSelectView()
        csv.update(0.016, (640, 360))
        csv.draw(surface)

        # 2. Map view
        dungeon_map = DungeonMap(num_floors=5, paths_per_floor=3)
        mv = MapView(dungeon_map, player)
        mv.update(0.016, (640, 360))
        mv.draw(surface)

        # 3. Reward view
        rw = RewardView(CombatReward(), player)
        rw.update(0.016, (640, 360))
        rw.draw(surface)

        # 4. Rest view
        rv = RestView(player)
        rv.update(0.016, (640, 360))
        rv.draw(surface)

        # 5. Shop view
        sv = ShopView(Shop(), player)
        sv.update(0.016, (640, 360))
        sv.draw(surface)

        # 6. Event view
        ev = EventView(generate_random_event(player), player)
        ev.update(0.016, (640, 360))
        ev.draw(surface)

        # 7. Deck view
        dv = DeckView(player)
        dv.update(0.016, (640, 360))
        dv.draw(surface)

        # 8. Game over view
        gov = GameOverView(True, player, 10)
        gov.update(0.016, (640, 360))
        gov.draw(surface)

    def test_game_coordinator_flow(self):
        """Simulate real gameplay loop via Game coordinator."""
        from main import Game
        from systems.save_manager import delete_save
        game = Game()
        self.assertEqual(game.state, "TITLE")
        game.current_view.update(0.016, (640, 360))
        game.current_view.draw(game.screen)

        # Transition to character select
        game.show_char_select()
        self.assertEqual(game.state, "CHAR_SELECT")
        game.current_view.update(0.016, (640, 360))
        game.current_view.draw(game.screen)

        # Start Blood Knight run
        game.start_run("blood_knight")
        self.assertEqual(game.state, "MAP")
        game.current_view.update(0.016, (640, 360))
        game.current_view.draw(game.screen)

        # Enter first node on map
        first_node = game.dungeon_map.floors[0][0]
        game.enter_node(first_node)
        self.assertEqual(game.state, "COMBAT")

        # Simulate 10 frames of combat loop
        for _ in range(10):
            game.current_view.update(0.016, (640, 360))
            game.current_view.draw(game.screen)

        # End player turn and simulate enemy turn frames
        game.combat_state.end_player_turn()
        self.assertEqual(game.combat_state.phase, "enemy_turn")
        for _ in range(10):
            game.current_view.update(0.016, (640, 360))
            game.current_view.draw(game.screen)

        delete_save(game.current_slot)

    def test_new_characters_tempest_and_templar(self):
        """Verifies Tempest Herald and Radiant Templar starters and relics."""
        # 1. Tempest Herald
        tempest = Player(char_id="tempest_herald")
        self.assertEqual(tempest.hp, 72)
        self.assertTrue(tempest.has_relic("storm_core"))
        tempest_cards = [c.name for c in tempest.deck]
        self.assertIn("Zap", tempest_cards)
        self.assertIn("Frost Barrier", tempest_cards)
        self.assertIn("Thunder Strike", tempest_cards)
        self.assertIn("Static Discharge", tempest_cards)

        # 2. Radiant Templar
        templar = Player(char_id="radiant_templar")
        self.assertEqual(templar.hp, 85)
        self.assertTrue(templar.has_relic("sun_crest"))
        templar_cards = [c.name for c in templar.deck]
        self.assertIn("Smite", templar_cards)
        self.assertIn("Holy Shield", templar_cards)
        self.assertIn("Consecration", templar_cards)
        self.assertIn("Radiant Vow", templar_cards)

    def test_new_cards_and_synergies(self):
        """Tests new cards like Zap, Thunder Strike, Judgment, Apotheosis, and Blizzard."""
        from models.card import (
            ZapCard, ThunderStrikeCard, JudgmentCard,
            ApotheosisCard, BlizzardCard, StrikeCard
        )
        player = Player(char_id="tempest_herald")
        enemy = CryptCultist()
        combat = CombatState(player, [enemy], self.particle_mgr, self.screen_shake)

        # 1. Zap applies Vulnerable
        zap = ZapCard()
        player.hand.append(zap)
        player.energy = 3
        combat.play_card(zap, enemy)
        self.assertTrue(enemy.statuses.has("Vulnerable"))

        # 2. Thunder Strike refunds 1 Energy if enemy has Vulnerable
        strike = ThunderStrikeCard()
        player.hand.append(strike)
        init_energy = player.energy
        combat.play_card(strike, enemy)
        # Cost is 1, refund is 1 -> net energy should remain equal
        self.assertEqual(player.energy, init_energy)

        # 3. Judgment: execution if <= 25 HP
        enemy.hp = 20
        judge = JudgmentCard()
        player.hand.append(judge)
        player.energy = 3
        combat.play_card(judge, enemy)
        self.assertFalse(enemy.is_alive())

        # 4. Apotheosis: upgrades entire deck
        c2 = CryptCultist()
        combat.enemies = [c2]
        combat.phase = "player_turn"
        s1 = StrikeCard()
        player.hand = [s1]
        apoth = ApotheosisCard()
        player.hand.append(apoth)
        player.energy = 3
        combat.play_card(apoth)
        self.assertTrue(s1.upgraded)

    def test_boss_relic_draft_and_act_ascension(self):
        """Verifies defeating a boss offers 3 Boss Relics and ascends to Act 2."""
        from systems.reward import CombatReward
        from views.reward_view import RewardView
        from main import Game

        game = Game()
        game.start_run("tempest_herald")
        self.assertEqual(game.current_act, 1)

        # Create Boss Reward
        reward = CombatReward(is_boss=True, act=game.current_act)
        self.assertTrue(len(reward.boss_relic_options) >= 3)
        self.assertEqual(reward.boss_relic_options[0].rarity, "Boss")

        # Choose a Boss Relic
        chosen_relic = reward.boss_relic_options[0]
        reward.choose_boss_relic(game.player, chosen_relic)
        self.assertTrue(game.player.has_relic(chosen_relic.id_name))
        self.assertTrue(reward.boss_relic_claimed)

        # Ascend to Act 2
        game.ascend_to_next_act()
        self.assertEqual(game.current_act, 2)
        self.assertEqual(game.dungeon_map.act, 2)
        self.assertIn("ACT II", game.dungeon_map.get_act_title())

    def test_act_2_and_3_enemies_behavior(self):
        """Verifies Act 2 and Act 3 enemies instantiate and execute correctly."""
        from models.enemy import (
            InfernalHound, ObsidianGolem, FlameArchon,
            CenturionAutomaton, IgnisTheInfernal, TheCorruptedHeart
        )
        player = Player(char_id="blood_knight")

        hound = InfernalHound()
        self.assertEqual(hound.hp, 48)

        golem = ObsidianGolem()
        self.assertEqual(golem.hp, 78)

        archon = FlameArchon()
        self.assertTrue(archon.is_elite)
        self.assertEqual(archon.statuses.get("Thorns"), 4)

        ignis = IgnisTheInfernal()
        self.assertTrue(ignis.is_boss)
        self.assertEqual(ignis.max_hp, 210)

        heart = TheCorruptedHeart()
        self.assertTrue(heart.is_boss)
        self.assertEqual(heart.max_hp, 320)

        # Test Combat execution against Heart
        combat = CombatState(player, [heart], self.particle_mgr, self.screen_shake)
        heart.decide_intent(combat)
        self.assertEqual(heart.intent.desc, "Blood Barrage (3x12)")
        heart.execute_turn(combat, player)
        self.assertTrue(player.hp < player.max_hp)

    def test_deck_view_scrolling_and_clamping(self):
        """Verifies DeckView scroll bounds, mouse wheel events, and smooth clamping."""
        from views.deck_view import DeckView
        from models.card import StrikeCard
        player = Player(char_id="blood_knight")
        # Add 24 extra cards so deck has 36 cards (6 rows)
        for _ in range(24):
            player.deck.append(StrikeCard())

        dv = DeckView(player)
        min_scroll = dv._get_max_scroll()
        self.assertTrue(min_scroll < 0)

        # Scroll down with mouse wheel event
        wheel_event = pygame.event.Event(pygame.MOUSEWHEEL, y=-3)
        dv.handle_event(wheel_event, (640, 360))
        self.assertTrue(dv.target_scroll_y < 0)

        # Update several ticks to verify smooth scroll interpolation
        for _ in range(15):
            dv.update(0.016, (640, 360))
        self.assertTrue(dv.scroll_y < 0)

        # Scroll far down to test clamp at min_scroll
        extreme_scroll = pygame.event.Event(pygame.MOUSEWHEEL, y=-100)
        dv.handle_event(extreme_scroll, (640, 360))
        self.assertEqual(dv.target_scroll_y, min_scroll)

        # Scroll up to test clamp at 0
        scroll_up = pygame.event.Event(pygame.MOUSEWHEEL, y=100)
        dv.handle_event(scroll_up, (640, 360))
        self.assertEqual(dv.target_scroll_y, 0.0)

    def test_rest_view_smith_scrolling_and_cancel(self):
        """Verifies RestView smithing scroll handling and Cancel button operation."""
        from views.rest_view import RestView
        from models.card import StrikeCard
        player = Player(char_id="blood_knight")
        for _ in range(20):
            player.deck.append(StrikeCard())

        rv = RestView(player)
        self.assertFalse(rv.smithing)

        # Click Smith button
        click_smith = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rv.smith_btn.rect.center)
        rv.handle_event(click_smith, rv.smith_btn.rect.center)
        self.assertTrue(rv.smithing)

        # Verify scroll bounds when smithing
        cards = rv._get_unupgraded_cards()
        min_scroll = rv._get_max_scroll(cards)
        self.assertTrue(min_scroll < 0)

        # Mouse wheel scroll
        wheel_down = pygame.event.Event(pygame.MOUSEWHEEL, y=-2)
        rv.handle_event(wheel_down, (640, 360))
        self.assertTrue(rv.target_scroll_y < 0)

        # Cancel smithing
        cancel_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rv.cancel_smith_btn.rect.center)
        rv.handle_event(cancel_click, rv.cancel_smith_btn.rect.center)
        self.assertFalse(rv.smithing)
        self.assertEqual(rv.scroll_y, 0.0)

    def test_shop_view_purge_scrolling_and_cancel(self):
        """Verifies ShopView card purge scrolling and Cancel button operation."""
        from views.shop_view import ShopView
        from systems.shop import Shop
        from models.card import StrikeCard
        player = Player(char_id="blood_knight")
        player.gold = 200
        for _ in range(20):
            player.deck.append(StrikeCard())

        shop = Shop()
        sv = ShopView(shop, player)
        self.assertFalse(sv.removing_card)

        # Click Remove Card button
        click_purge = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=sv.remove_card_btn.rect.center)
        sv.handle_event(click_purge, sv.remove_card_btn.rect.center)
        self.assertTrue(sv.removing_card)

        # Verify scroll bounds
        min_scroll = sv._get_max_scroll()
        self.assertTrue(min_scroll < 0)

        # Mouse wheel scroll
        wheel_down = pygame.event.Event(pygame.MOUSEWHEEL, y=-3)
        sv.handle_event(wheel_down, (640, 360))
        self.assertTrue(sv.target_scroll_y < 0)

        # Click cancel
        cancel_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=sv.cancel_remove_btn.rect.center)
        sv.handle_event(cancel_click, sv.cancel_remove_btn.rect.center)
        self.assertFalse(sv.removing_card)
        self.assertEqual(sv.scroll_y, 0.0)

    def test_save_manager_save_and_load(self):
        """Verifies full roundtrip serialization of player, cards, relics, potions, and map."""
        from systems.save_manager import save_game, load_game, delete_save, get_slot_info
        from systems.map_generator import DungeonMap

        slot = 3
        delete_save(slot)

        player = Player(char_id="shadow_assassin")
        player.hp = 54
        player.gold = 320
        player.deck[0].upgrade()
        player.deck[1].upgrade()

        dungeon_map = DungeonMap(num_floors=10, paths_per_floor=3, act=2)
        node = dungeon_map.floors[0][1]
        dungeon_map.select_node(node)

        self.assertTrue(save_game(slot, player, dungeon_map, current_act=2))

        info = get_slot_info(slot)
        self.assertTrue(info["exists"])
        self.assertEqual(info["char_id"], "shadow_assassin")
        self.assertEqual(info["hp"], 54)
        self.assertEqual(info["gold"], 320)
        self.assertEqual(info["act"], 2)

        loaded = load_game(slot)
        self.assertIsNotNone(loaded)
        p2 = loaded["player"]
        m2 = loaded["dungeon_map"]

        self.assertEqual(p2.char_id, "shadow_assassin")
        self.assertEqual(p2.hp, 54)
        self.assertEqual(p2.gold, 320)
        self.assertTrue(p2.deck[0].upgraded)
        self.assertTrue(p2.deck[1].upgraded)
        self.assertEqual(m2.act, 2)
        self.assertEqual(m2.current_node.floor, 0)
        self.assertEqual(m2.current_node.index, 1)

        delete_save(slot)
        self.assertFalse(get_slot_info(slot)["exists"])

    def test_title_view_and_navigation(self):
        """Verifies TitleView rendering, button states, and event handling."""
        from views.title_view import TitleView
        from systems.save_manager import save_game, delete_save
        from systems.map_generator import DungeonMap

        # Clear slot 1 and check title view with no saves
        delete_save(1)
        delete_save(2)
        delete_save(3)

        tv = TitleView()
        self.assertFalse(tv.has_save)
        self.assertFalse(tv.continue_btn.enabled)

        # Draw and update TitleView
        surf = pygame.Surface((1280, 720))
        tv.update(0.016, (640, 360))
        tv.draw(surf)

        # Click New Expedition
        click_new = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tv.new_run_btn.rect.center)
        action, data = tv.handle_event(click_new, tv.new_run_btn.rect.center)
        self.assertEqual(action, "new_run")

        # Now save a game in slot 1 and refresh
        p = Player(char_id="blood_knight")
        m = DungeonMap(num_floors=10, paths_per_floor=3, act=1)
        save_game(1, p, m, 1)

        tv.refresh_save_status()
        self.assertTrue(tv.has_save)
        self.assertTrue(tv.continue_btn.enabled)

        # Click Continue
        click_cont = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tv.continue_btn.rect.center)
        action, data = tv.handle_event(click_cont, tv.continue_btn.rect.center)
        self.assertEqual(action, "continue")
        self.assertEqual(data, 1)

        # Cleanup
        delete_save(1)

    def test_load_game_view_interactions(self):
        """Verifies LoadGameView slot browsing, resuming, and safe deletion."""
        from views.load_game_view import LoadGameView
        from systems.save_manager import save_game, delete_save
        from systems.map_generator import DungeonMap

        delete_save(1)
        delete_save(2)
        delete_save(3)

        # Create save in slot 2
        p = Player(char_id="tempest_herald")
        m = DungeonMap(num_floors=10, paths_per_floor=3, act=1)
        save_game(2, p, m, 1)

        lgv = LoadGameView()
        surf = pygame.Surface((1280, 720))
        lgv.update(0.016, (640, 360))
        lgv.draw(surf)

        # Slot 1 is empty -> clicking start run
        btn_s1 = lgv.slot_buttons[1]["new"]
        click_s1 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=btn_s1.rect.center)
        action, sid = lgv.handle_event(click_s1, btn_s1.rect.center)
        self.assertEqual(action, "new_run_slot")
        self.assertEqual(sid, 1)

        # Slot 2 has save -> clicking resume
        btn_s2_load = lgv.slot_buttons[2]["load"]
        click_s2 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=btn_s2_load.rect.center)
        action, sid = lgv.handle_event(click_s2, btn_s2_load.rect.center)
        self.assertEqual(action, "load_slot")
        self.assertEqual(sid, 2)

        # Slot 2 delete flow: first click prompts confirmation, second confirms
        btn_s2_del = lgv.slot_buttons[2]["delete"]
        click_del1 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=btn_s2_del.rect.center)
        action, sid = lgv.handle_event(click_del1, btn_s2_del.rect.center)
        self.assertEqual(action, "none")
        self.assertEqual(lgv.confirm_delete_slot, 2)

        # Second click deletes
        btn_s2_del_conf = lgv.slot_buttons[2]["delete"]
        click_del2 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=btn_s2_del_conf.rect.center)
        action, sid = lgv.handle_event(click_del2, btn_s2_del_conf.rect.center)
        self.assertIsNone(lgv.confirm_delete_slot)
        self.assertFalse(lgv.slots[1]["exists"])

    def test_game_save_and_quit_flow(self):
        """Verifies end-to-end saving from MapView, returning to TitleView, and reloading."""
        from main import Game
        from systems.save_manager import delete_save, get_slot_info

        delete_save(1)
        game = Game()
        self.assertEqual(game.state, "TITLE")

        # Start a new run
        game.start_run("void_necromancer", slot_id=1)
        self.assertEqual(game.state, "MAP")
        game.player.gold = 500

        # Click Save & Quit on map view
        save_btn_pos = game.map_view.save_btn_rect.center
        click_save = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=save_btn_pos)
        action, _ = game.map_view.handle_event(click_save, save_btn_pos)
        self.assertEqual(action, "save_and_quit")

        # Simulate coordinator handling
        game.save_current_run()
        game.show_title_screen()
        self.assertEqual(game.state, "TITLE")

        # Verify save exists
        info = get_slot_info(1)
        self.assertTrue(info["exists"])
        self.assertEqual(info["gold"], 500)

        # Load run
        game.load_run(1)
        self.assertEqual(game.state, "MAP")
        self.assertEqual(game.player.gold, 500)
        self.assertEqual(game.player.char_id, "void_necromancer")

        # Clean up
        delete_save(1)

if __name__ == "__main__":
    unittest.main()




