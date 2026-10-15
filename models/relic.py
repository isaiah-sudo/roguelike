"""
Relics system with hooks for passive abilities and character starter relics.
"""
import random
from typing import Optional

class Relic:
    def __init__(self, id_name: str, name: str, description: str, rarity: str = "Common"):
        self.id_name = id_name
        self.name = name
        self.description = description
        self.rarity = rarity
        self.counter = 0

    def on_combat_start(self, combat_state, player):
        pass

    def on_turn_start(self, combat_state, player, turn_number: int):
        pass

    def on_turn_end(self, combat_state, player):
        pass

    def on_card_played(self, combat_state, player, card):
        pass

    def on_card_exhausted(self, combat_state, player, card):
        pass

    def on_combat_end(self, combat_state, player, won: bool):
        pass

# ==========================================
# CHARACTER STARTER RELICS
# ==========================================

class BurningBloodRelic(Relic):
    def __init__(self):
        super().__init__("burning_blood", "Burning Blood", "At the end of combat, heal 6 HP.", "Starter")

    def on_combat_end(self, combat_state, player, won: bool):
        if won:
            player.heal(6)

class RingOfTheSerpentRelic(Relic):
    def __init__(self):
        super().__init__("ring_serpent", "Serpent Ring", "At start of combat, draw 2 additional cards.", "Starter")

    def on_combat_start(self, combat_state, player):
        player.draw_cards(2)

class SoulPhylacteryRelic(Relic):
    def __init__(self):
        super().__init__("soul_phylactery", "Soul Phylactery", "Whenever a card is Exhausted, deal 4 damage to a random enemy.", "Starter")

    def on_card_exhausted(self, combat_state, player, card):
        alive = [e for e in combat_state.enemies if e.is_alive()]
        if alive:
            target = random.choice(alive)
            target.take_damage(4, is_attack=False)
            combat_state.particle_mgr.spawn_popup(target.x + 30, target.y + 20, "-4 Soul", (180, 80, 240))

class StormCoreRelic(Relic):
    def __init__(self):
        super().__init__("storm_core", "Cracked Storm Core", "At the end of your turn, zap a random enemy for 5 damage.", "Starter")

    def on_turn_end(self, combat_state, player):
        alive = [e for e in combat_state.enemies if e.is_alive()]
        if alive:
            target = random.choice(alive)
            target.take_damage(5, is_attack=False)
            combat_state.particle_mgr.spawn_popup(target.x + 30, target.y + 20, "-5 Zap", (80, 200, 255))
            from engine.sound import play_sfx
            play_sfx('magic', 0.6)

class SunCrestRelic(Relic):
    def __init__(self):
        super().__init__("sun_crest", "Sun Crest", "Whenever you play a Skill, gain 1 Retribution (Thorns).", "Starter")

    def on_card_played(self, combat_state, player, card):
        from models.card import CardType
        if card.card_type == CardType.SKILL:
            player.statuses.apply("Thorns", 1)
            combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

# ==========================================
# DUNGEON RELICS
# ==========================================

class VajraRelic(Relic):
    def __init__(self):
        super().__init__("vajra", "Vajra", "Start each combat with 1 Strength.")

    def on_combat_start(self, combat_state, player):
        player.statuses.apply("Strength", 1)

class AnchorRelic(Relic):
    def __init__(self):
        super().__init__("anchor", "Anchor", "Start each combat with 10 Block.")

    def on_combat_start(self, combat_state, player):
        player.gain_block(10)

class LanternRelic(Relic):
    def __init__(self):
        super().__init__("lantern", "Lantern", "Gain 1 additional Energy on Turn 1.")

    def on_turn_start(self, combat_state, player, turn_number: int):
        if turn_number == 1:
            player.energy += 1

class BloodVialRelic(Relic):
    def __init__(self):
        super().__init__("blood_vial", "Blood Vial", "At the start of combat, heal 4 HP.")

    def on_combat_start(self, combat_state, player):
        player.heal(4)

class MeatOnTheBoneRelic(Relic):
    def __init__(self):
        super().__init__("meat_bone", "Meat Bone", "If your HP is at or below 50% at the end of combat, heal 12 HP.")

    def on_combat_end(self, combat_state, player, won: bool):
        if won and player.hp <= player.max_hp // 2:
            player.heal(12)

class KunaiRelic(Relic):
    def __init__(self):
        super().__init__("kunai", "Kunai", "Every time you play 3 Attacks in a single turn, gain 1 Dexterity.")
        self.attacks_played = 0

    def on_turn_start(self, combat_state, player, turn_number: int):
        self.attacks_played = 0

    def on_card_played(self, combat_state, player, card):
        from models.card import CardType
        if card.card_type == CardType.ATTACK:
            self.attacks_played += 1
            if self.attacks_played % 3 == 0:
                player.statuses.apply("Dexterity", 1)

class DarkGrimoireRelic(Relic):
    def __init__(self):
        super().__init__("dark_grimoire", "Grimoire", "Draw 1 additional card at the start of each turn.")

    def on_turn_start(self, combat_state, player, turn_number: int):
        player.draw_cards(1)

class TwistedFunnelRelic(Relic):
    def __init__(self):
        super().__init__("twisted_funnel", "Twisted Funnel", "At start of combat, apply 4 Poison to ALL enemies.")

    def on_combat_start(self, combat_state, player):
        for e in combat_state.enemies:
            if e.is_alive():
                e.statuses.apply("Poison", 4)
                combat_state.spawn_poison_fx(e.x + e.width // 2, e.y + e.height // 2)

class PreservedInsectRelic(Relic):
    def __init__(self):
        super().__init__("preserved_insect", "Preserved Insect", "Elites have 25% reduced Max HP in combat.")

    def on_combat_start(self, combat_state, player):
        for e in combat_state.enemies:
            if getattr(e, 'is_elite', False):
                reduction = int(e.max_hp * 0.25)
                e.max_hp = max(1, e.max_hp - reduction)
                e.hp = min(e.hp, e.max_hp)

class CaptainWheelRelic(Relic):
    def __init__(self):
        super().__init__("captain_wheel", "Captain's Wheel", "On Turn 3, gain 18 Block.")

    def on_turn_start(self, combat_state, player, turn_number: int):
        if turn_number == 3:
            player.gain_block(18)
            combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class CentennialPuzzleRelic(Relic):
    def __init__(self):
        super().__init__("centennial_puzzle", "Centennial Puzzle", "The first time you take damage in combat, draw 3 cards.")
        self.triggered = False

    def on_combat_start(self, combat_state, player):
        self.triggered = False

    def on_card_played(self, combat_state, player, card):
        if not self.triggered and combat_state.times_player_damaged > 0:
            self.triggered = True
            player.draw_cards(3)

# ==========================================
# BOSS RELICS
# ==========================================

class PhilosophersStoneRelic(Relic):
    def __init__(self):
        super().__init__("philosophers_stone", "Philosopher's Stone", "Gain 1 Energy every turn. ALL enemies gain 1 Strength.", "Boss")

    def on_combat_start(self, combat_state, player):
        player.energy += 1
        for e in combat_state.enemies:
            if e.is_alive():
                e.statuses.apply("Strength", 1)

    def on_turn_start(self, combat_state, player, turn_number: int):
        player.energy += 1

class EnergyCoreRelic(Relic):
    def __init__(self):
        super().__init__("energy_core", "Energy Core", "Gain 1 additional Energy at the start of each turn.", "Boss")

    def on_turn_start(self, combat_state, player, turn_number: int):
        player.energy += 1

class RunicPyramidRelic(Relic):
    def __init__(self):
        super().__init__("runic_pyramid", "Runic Pyramid", "At end of turn, do not discard your hand.", "Boss")

class SneckoEyeRelic(Relic):
    def __init__(self):
        super().__init__("snecko_eye", "Snecko Eye", "Draw 2 additional cards each turn. Costs become erratic.", "Boss")

    def on_turn_start(self, combat_state, player, turn_number: int):
        player.draw_cards(2)

class BlackStarRelic(Relic):
    def __init__(self):
        super().__init__("black_star", "Black Star", "Elites drop an additional Relic upon defeat.", "Boss")

class HolyGrailRelic(Relic):
    def __init__(self):
        super().__init__("holy_grail", "Holy Grail", "At the end of combat, heal 15 HP.", "Boss")

    def on_combat_end(self, combat_state, player, won: bool):
        if won:
            player.heal(15)

class AstrolabeRelic(Relic):
    def __init__(self):
        super().__init__("astrolabe", "Astrolabe", "Upon pickup, upgrade 3 random cards in your deck.", "Boss")

    def on_pickup(self, player):
        unupgraded = [c for c in player.deck if not c.upgraded]
        selected = random.sample(unupgraded, min(3, len(unupgraded)))
        for c in selected:
            c.upgrade()

ALL_RELIC_CLASSES = [
    VajraRelic, AnchorRelic, LanternRelic, BloodVialRelic,
    MeatOnTheBoneRelic, KunaiRelic, DarkGrimoireRelic, TwistedFunnelRelic,
    PreservedInsectRelic, CaptainWheelRelic, CentennialPuzzleRelic
]

BOSS_RELIC_CLASSES = [
    PhilosophersStoneRelic, EnergyCoreRelic, RunicPyramidRelic,
    SneckoEyeRelic, BlackStarRelic, HolyGrailRelic, AstrolabeRelic
]
