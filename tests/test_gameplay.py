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
        game = Game()
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

if __name__ == "__main__":
    unittest.main()



