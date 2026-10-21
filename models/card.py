"""
Comprehensive Dark Fantasy Card Library with deep archetype synergies and combos:
- 0-Cost Buffs, Cantrips & Enablers (Flex, Adrenaline, Seeing Red, Warcry, Shadowstep, Gouge, Offering)
- Blood & Self-Harm Berserker (Hemokinesis, Rupture, Combustion, Blood for Blood, Reaper)
- Shiv Tempo & Finisher Chains (Accuracy, Blade Dance, Storm of Steel, Finisher, Double Tap, Burst, Backflip)
- Exponential Poison & Decay (Deadly Poison, Bouncing Flask, Crippling Cloud, Corpse Explosion, Catalyst, Noxious Fumes)
- Fortress Block & Shield Slam (Body Slam, Entrench, Flame Barrier, Barricade, Impervious)
- Necromantic Exhaust Engines (Feel No Pain, Dark Embrace, Corruption, Second Wind, Sever Soul, Exhumation)
"""
from enum import Enum
import copy
import random

class CardType(Enum):
    ATTACK = "Attack"
    SKILL = "Skill"
    POWER = "Power"
    CURSE = "Curse"

class CardRarity(Enum):
    STARTER = "Starter"
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    SPECIAL = "Special"

class TargetType(Enum):
    ENEMY = "enemy"
    ALL_ENEMIES = "all_enemies"
    SELF = "self"

class Card:
    character: str | None = None

    def __init__(self, id_name: str, name: str, cost: int, card_type: CardType,
                 rarity: CardRarity, target_type: TargetType, description: str,
                 exhaust: bool = False, innate: bool = False, character: str | None = None):
        self.id_name = id_name
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.rarity = rarity
        self.target_type = target_type
        self.description = description
        self.exhaust = True if card_type == CardType.POWER else exhaust
        self.innate = innate
        self.character = character if character is not None else getattr(self.__class__, 'character', None)
        self.upgraded = False

    def clone(self):
        return copy.deepcopy(self)

    def upgrade(self):
        if not self.upgraded:
            self.upgraded = True
            self.name += "+"
            self.apply_upgrade()

    def apply_upgrade(self):
        pass

    def get_calculated_damage(self, player, base_dmg: int, str_multiplier: int = 1) -> int:
        strength = player.statuses.get("Strength")
        weak = player.statuses.get("Weak") > 0
        total = max(0, base_dmg + strength * str_multiplier)
        if weak:
            total = int(total * 0.75)
        return total

    def get_calculated_block(self, player, base_block: int) -> int:
        dex = player.statuses.get("Dexterity")
        return max(0, base_block + dex)

    def play(self, combat_state, player, target=None):
        raise NotImplementedError

# ==========================================
# 1. STARTER CARDS
# ==========================================

class StrikeCard(Card):
    def __init__(self):
        super().__init__("strike", "Strike", 1, CardType.ATTACK, CardRarity.STARTER,
                         TargetType.ENEMY, "Deal 6 damage.")
        self.damage = 6

    def apply_upgrade(self):
        self.damage = 9
        self.description = "Deal 9 damage."

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg)

class DefendCard(Card):
    def __init__(self):
        super().__init__("defend", "Defend", 1, CardType.SKILL, CardRarity.STARTER,
                         TargetType.SELF, "Gain 5 Block.")
        self.block_val = 5

    def apply_upgrade(self):
        self.block_val = 8
        self.description = "Gain 8 Block."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class BashCard(Card):
    def __init__(self):
        super().__init__("bash", "Bash", 2, CardType.ATTACK, CardRarity.STARTER,
                         TargetType.ENEMY, "Deal 8 damage. Apply 2 Vulnerable.")
        self.damage = 8
        self.vulnerable = 2

    def apply_upgrade(self):
        self.damage = 10
        self.vulnerable = 3
        self.description = "Deal 10 damage. Apply 3 Vulnerable."

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg)
            target.statuses.apply("Vulnerable", self.vulnerable)

# ==========================================
# 2. 0-COST BUFFS, CANTRIPS & COMBO ENABLERS
# ==========================================

class AdrenalineCard(Card):
    def __init__(self):
        super().__init__("adrenaline", "Adrenaline", 0, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "Gain 1 Energy. Draw 2 cards. Exhaust.", exhaust=True)
        self.energy_gain = 1

    def apply_upgrade(self):
        self.energy_gain = 2
        self.description = "Gain 2 Energy. Draw 2 cards. Exhaust."

    def play(self, combat_state, player, target=None):
        player.energy += self.energy_gain
        player.draw_cards(2)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class FlexCard(Card):
    def __init__(self):
        super().__init__("flex", "Flex", 0, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 2 Strength. At turn end, lose 2 Strength.")
        self.str_amt = 2

    def apply_upgrade(self):
        self.str_amt = 4
        self.description = "Gain 4 Strength. At turn end, lose 4 Strength."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Strength", self.str_amt)
        player.statuses.apply("FlexStrength", self.str_amt)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class BattleTranceCard(Card):
    def __init__(self):
        super().__init__("battle_trance", "Battle Trance", 0, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Draw 3 cards.")
        self.draw_count = 3

    def apply_upgrade(self):
        self.draw_count = 4
        self.description = "Draw 4 cards."

    def play(self, combat_state, player, target=None):
        player.draw_cards(self.draw_count)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class SeeingRedCard(Card):
    def __init__(self):
        super().__init__("seeing_red", "Seeing Red", 0, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Gain 2 Energy. Exhaust.", exhaust=True)
        self.energy_gain = 2

    def apply_upgrade(self):
        self.energy_gain = 3
        self.description = "Gain 3 Energy. Exhaust."

    def play(self, combat_state, player, target=None):
        player.energy += self.energy_gain
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class WarcryCard(Card):
    def __init__(self):
        super().__init__("warcry", "Warcry", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 6 Block. Draw 1 card.")
        self.draw_count = 1
        self.block_val = 6

    def apply_upgrade(self):
        self.draw_count = 2
        self.block_val = 9
        self.description = "Gain 9 Block. Draw 2 cards."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        player.draw_cards(self.draw_count)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class ShadowstepCard(Card):
    def __init__(self):
        super().__init__("shadowstep", "Shadowstep", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 6 Block. Draw 1 card.")
        self.block_val = 6
        self.draw_count = 1

    def apply_upgrade(self):
        self.block_val = 9
        self.draw_count = 2
        self.description = "Gain 9 Block. Draw 2 cards."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        player.draw_cards(self.draw_count)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class GougeCard(Card):
    def __init__(self):
        super().__init__("gouge", "Gouge", 0, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, "Deal 4 damage. Apply 1 Vulnerable.")
        self.damage = 4
        self.vuln = 1

    def apply_upgrade(self):
        self.damage = 6
        self.vuln = 2
        self.description = "Deal 6 damage. Apply 2 Vulnerable."

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg)
            target.statuses.apply("Vulnerable", self.vuln)

class OfferingCard(Card):
    def __init__(self):
        super().__init__("offering", "Dark Offering", 0, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "Lose 3 HP. Gain 2 Energy. Draw 3 cards. Exhaust.", exhaust=True)
        self.draw_count = 3

    def apply_upgrade(self):
        self.draw_count = 5
        self.description = "Lose 3 HP. Gain 2 Energy. Draw 5 cards. Exhaust."

    def play(self, combat_state, player, target=None):
        combat_state.player_take_card_damage(3)
        player.energy += 2
        player.draw_cards(self.draw_count)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class ShivCard(Card):
    def __init__(self):
        super().__init__("shiv", "Shiv", 0, CardType.ATTACK, CardRarity.SPECIAL,
                         TargetType.ENEMY, "Deal 4 damage. Exhaust.", exhaust=True)
        self.damage = 4

    def apply_upgrade(self):
        self.damage = 6
        self.description = "Deal 6 damage. Exhaust."

    def play(self, combat_state, player, target=None):
        if target:
            # Accuracy power adds bonus to shivs
            acc = player.statuses.get("Accuracy")
            base = self.damage + acc
            dmg = self.get_calculated_damage(player, base)
            combat_state.deal_attack_damage(player, target, dmg)

# ==========================================
# 3. BLOOD & SELF-HARM BERSERKER SYNERGIES
# ==========================================

class HemokinesisCard(Card):
    def __init__(self):
        super().__init__("hemokinesis", "Hemokinesis", 1, CardType.ATTACK, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Lose 2 HP. Deal 15 damage.")
        self.damage = 15

    def apply_upgrade(self):
        self.damage = 20
        self.description = "Lose 2 HP. Deal 20 damage."

    def play(self, combat_state, player, target=None):
        combat_state.player_take_card_damage(2)
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg, heavy=True)

class RuptureCard(Card):
    def __init__(self):
        super().__init__("rupture", "Rupture", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "Whenever you lose HP from a card, gain 1 Strength.")
        self.str_gain = 1

    def apply_upgrade(self):
        self.str_gain = 2
        self.description = "Whenever you lose HP from a card, gain 2 Strength."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Rupture", self.str_gain)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class CombustionCard(Card):
    def __init__(self):
        super().__init__("combustion", "Combustion", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "At turn end, lose 1 HP and deal 5 damage to ALL enemies.")
        self.burn_dmg = 5

    def apply_upgrade(self):
        self.burn_dmg = 7
        self.description = "At turn end, lose 1 HP and deal 7 damage to ALL enemies."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Combustion", self.burn_dmg)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class BloodForBloodCard(Card):
    def __init__(self):
        super().__init__("blood_for_blood", "Blood For Blood", 4, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ENEMY, "Costs 1 less for each time you took damage. Deal 18 damage.")
        self.damage = 18

    def apply_upgrade(self):
        self.damage = 24
        self.description = "Costs 1 less for each time you took damage. Deal 24 damage."

    def get_dynamic_cost(self, combat_state):
        discount = combat_state.times_player_damaged
        return max(0, self.cost - discount)

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg, heavy=True)

class HeavyBladeCard(Card):
    def __init__(self):
        super().__init__("heavy_blade", "Heavy Blade", 2, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, "Deal 14 damage. Strength affects this 3x.")
        self.damage = 14
        self.str_mult = 3

    def apply_upgrade(self):
        self.str_mult = 5
        self.description = "Deal 14 damage. Strength affects this 5x."

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage, self.str_mult)
            combat_state.deal_attack_damage(player, target, dmg, heavy=True)

class ReaperCard(Card):
    def __init__(self):
        super().__init__("reaper", "Soul Reaper", 2, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ALL_ENEMIES, "Deal 5 damage to ALL enemies. Heal unblocked damage. Exhaust.", exhaust=True)
        self.damage = 5

    def apply_upgrade(self):
        self.damage = 7
        self.description = "Deal 7 damage to ALL enemies. Heal unblocked damage. Exhaust."

    def play(self, combat_state, player, target=None):
        dmg = self.get_calculated_damage(player, self.damage)
        total_healed = 0
        for enemy in combat_state.enemies:
            if enemy.is_alive():
                hp_dmg, _ = combat_state.deal_attack_damage(player, enemy, dmg)
                total_healed += hp_dmg
        if total_healed > 0:
            player.heal(total_healed)

# ==========================================
# 4. SHIV TEMPO & COMBO MULTI-CAST
# ==========================================

class BladeDanceCard(Card):
    def __init__(self):
        super().__init__("blade_dance", "Blade Dance", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Add 3 Shivs to your hand.")
        self.count = 3

    def apply_upgrade(self):
        self.count = 4
        self.description = "Add 4 Shivs to your hand."

    def play(self, combat_state, player, target=None):
        for _ in range(self.count):
            player.add_card_to_hand(ShivCard())

class CloakAndDaggerCard(Card):
    def __init__(self):
        super().__init__("cloak_and_dagger", "Cloak & Dagger", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 6 Block. Add 1 Shiv to your hand.")
        self.block_val = 6
        self.shiv_count = 1

    def apply_upgrade(self):
        self.block_val = 9
        self.shiv_count = 2
        self.description = "Gain 9 Block. Add 2 Shivs to your hand."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)
        for _ in range(self.shiv_count):
            player.add_card_to_hand(ShivCard())

class AccuracyCard(Card):
    def __init__(self):
        super().__init__("accuracy", "Accuracy", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "Shivs deal 4 additional damage.")
        self.bonus = 4

    def apply_upgrade(self):
        self.bonus = 6
        self.description = "Shivs deal 6 additional damage."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Accuracy", self.bonus)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class InfiniteBladesCard(Card):
    def __init__(self):
        super().__init__("infinite_blades", "Infinite Blades", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "At the start of your turn, add 1 Shiv to hand.")

    def apply_upgrade(self):
        self.cost = 0
        self.description = "At the start of your turn, add 1 Shiv to hand."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("InfiniteBlades", 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class StormOfSteelCard(Card):
    def __init__(self):
        super().__init__("storm_of_steel", "Storm of Steel", 1, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "Discard your hand. Add that many Shivs to hand.")

    def apply_upgrade(self):
        self.description = "Discard your hand. Add that many upgraded Shiv+ to hand."

    def play(self, combat_state, player, target=None):
        count = len(player.hand)
        player.discard_hand()
        for _ in range(count):
            shiv = ShivCard()
            if self.upgraded:
                shiv.upgrade()
            player.add_card_to_hand(shiv)

class FinisherCard(Card):
    def __init__(self):
        super().__init__("finisher", "Finisher", 1, CardType.ATTACK, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Deal 6 damage for EACH Attack played this turn.")
        self.damage_per_attack = 6

    def apply_upgrade(self):
        self.damage_per_attack = 9
        self.description = "Deal 9 damage for EACH Attack played this turn."

    def play(self, combat_state, player, target=None):
        if target:
            attacks_played = combat_state.attacks_played_this_turn
            total_hits = max(1, attacks_played)
            dmg = self.get_calculated_damage(player, self.damage_per_attack)
            for _ in range(total_hits):
                if target.is_alive():
                    combat_state.deal_attack_damage(player, target, dmg)

class DoubleTapCard(Card):
    def __init__(self):
        super().__init__("double_tap", "Double Tap", 1, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "This turn, your next Attack is played twice.")
        self.charges = 1

    def apply_upgrade(self):
        self.charges = 2
        self.description = "This turn, your next 2 Attacks are played twice."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("DoubleTap", self.charges)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class BurstCard(Card):
    def __init__(self):
        super().__init__("burst", "Burst", 1, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "This turn, your next Skill is played twice.")
        self.charges = 1

    def apply_upgrade(self):
        self.charges = 2
        self.description = "This turn, your next 2 Skills are played twice."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Burst", self.charges)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class BackflipCard(Card):
    def __init__(self):
        super().__init__("backflip", "Backflip", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 5 Block. Draw 2 cards.")
        self.block_val = 5

    def apply_upgrade(self):
        self.block_val = 8
        self.description = "Gain 8 Block. Draw 2 cards."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        player.draw_cards(2)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

# ==========================================
# 5. POISON & EXPONENTIAL DECAY SYNERGIES
# ==========================================

class DeadlyPoisonCard(Card):
    def __init__(self):
        super().__init__("deadly_poison", "Deadly Poison", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.ENEMY, "Apply 5 Poison.")
        self.poison = 5

    def apply_upgrade(self):
        self.poison = 7
        self.description = "Apply 7 Poison."

    def play(self, combat_state, player, target=None):
        if target:
            target.statuses.apply("Poison", self.poison)
            combat_state.spawn_poison_fx(target.x + target.width // 2, target.y + target.height // 2)

class BouncingFlaskCard(Card):
    def __init__(self):
        super().__init__("bouncing_flask", "Bouncing Flask", 2, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.ALL_ENEMIES, "Apply 3 Poison to a random enemy 3 times.")
        self.bounces = 3

    def apply_upgrade(self):
        self.bounces = 4
        self.description = "Apply 3 Poison to a random enemy 4 times."

    def play(self, combat_state, player, target=None):
        alive_enemies = [e for e in combat_state.enemies if e.is_alive()]
        if not alive_enemies:
            return
        for _ in range(self.bounces):
            alive_enemies = [e for e in combat_state.enemies if e.is_alive()]
            if alive_enemies:
                chosen = random.choice(alive_enemies)
                chosen.statuses.apply("Poison", 3)
                combat_state.spawn_poison_fx(chosen.x + chosen.width // 2, chosen.y + chosen.height // 2)

class CripplingCloudCard(Card):
    def __init__(self):
        super().__init__("crippling_cloud", "Crippling Cloud", 2, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.ALL_ENEMIES, "Apply 4 Poison and 2 Weak to ALL enemies. Exhaust.", exhaust=True)
        self.poison = 4

    def apply_upgrade(self):
        self.poison = 7
        self.description = "Apply 7 Poison and 2 Weak to ALL enemies. Exhaust."

    def play(self, combat_state, player, target=None):
        for enemy in combat_state.enemies:
            if enemy.is_alive():
                enemy.statuses.apply("Poison", self.poison)
                enemy.statuses.apply("Weak", 2)
                combat_state.spawn_poison_fx(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2)

class CorpseExplosionCard(Card):
    def __init__(self):
        super().__init__("corpse_explosion", "Corpse Explosion", 2, CardType.SKILL, CardRarity.RARE,
                         TargetType.ENEMY, "Apply 6 Poison. When target dies, it deals its Max HP to ALL remaining enemies.")
        self.poison = 6

    def apply_upgrade(self):
        self.poison = 9
        self.description = "Apply 9 Poison. When target dies, it deals its Max HP to ALL remaining enemies."

    def play(self, combat_state, player, target=None):
        if target:
            target.statuses.apply("Poison", self.poison)
            target.statuses.apply("CorpseExplosion", 1)
            combat_state.spawn_poison_fx(target.x + target.width // 2, target.y + target.height // 2)

class CatalystCard(Card):
    def __init__(self):
        super().__init__("catalyst", "Catalyst", 1, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Double enemy's Poison. Exhaust.", exhaust=True)
        self.multiplier = 2

    def apply_upgrade(self):
        self.multiplier = 3
        self.description = "Triple enemy's Poison. Exhaust."

    def play(self, combat_state, player, target=None):
        if target and target.statuses.has("Poison"):
            current = target.statuses.get("Poison")
            target.statuses.apply("Poison", current * (self.multiplier - 1))
            combat_state.spawn_poison_fx(target.x + target.width // 2, target.y + target.height // 2)

class NoxiousFumesCard(Card):
    def __init__(self):
        super().__init__("noxious_fumes", "Noxious Fumes", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "At start of turn, apply 2 Poison to ALL enemies.")
        self.poison = 2

    def apply_upgrade(self):
        self.poison = 3
        self.description = "At start of turn, apply 3 Poison to ALL enemies."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("NoxiousFumes", self.poison)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

# ==========================================
# 6. FORTRESS BLOCK & SHIELD SLAM SYNERGIES
# ==========================================

class BodySlamCard(Card):
    def __init__(self):
        super().__init__("body_slam", "Body Slam", 1, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, "Deal damage equal to your current Block.")

    def apply_upgrade(self):
        self.cost = 0
        self.description = "Deal damage equal to your current Block."

    def play(self, combat_state, player, target=None):
        if target:
            block_damage = player.block
            dmg = self.get_calculated_damage(player, block_damage)
            combat_state.deal_attack_damage(player, target, dmg, heavy=True)

class EntrenchCard(Card):
    def __init__(self):
        super().__init__("entrench", "Entrench", 2, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Double your current Block.")

    def apply_upgrade(self):
        self.cost = 1
        self.description = "Double your current Block."

    def play(self, combat_state, player, target=None):
        current_block = player.block
        if current_block > 0:
            player.gain_block(current_block)
            combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class FlameBarrierCard(Card):
    def __init__(self):
        super().__init__("flame_barrier", "Flame Barrier", 2, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Gain 12 Block. When attacked this turn, deal 4 damage back.")
        self.block_val = 12
        self.retaliation = 4

    def apply_upgrade(self):
        self.block_val = 16
        self.retaliation = 6
        self.description = "Gain 16 Block. When attacked this turn, deal 6 damage back."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        player.statuses.apply("FlameBarrier", self.retaliation)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class BarricadeCard(Card):
    def __init__(self):
        super().__init__("barricade", "Barricade", 3, CardType.POWER, CardRarity.RARE,
                         TargetType.SELF, "Block is not removed at the start of your turn.")

    def apply_upgrade(self):
        self.cost = 2
        self.description = "Block is not removed at the start of your turn."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Barricade", 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class ImperviousCard(Card):
    def __init__(self):
        super().__init__("impervious", "Impervious", 2, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "Gain 30 Block. Exhaust.", exhaust=True)
        self.block_val = 30

    def apply_upgrade(self):
        self.block_val = 40
        self.description = "Gain 40 Block. Exhaust."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class IronWaveCard(Card):
    def __init__(self):
        super().__init__("iron_wave", "Iron Wave", 1, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, "Gain 5 Block. Deal 5 damage.")
        self.damage = 5
        self.block_val = 5

    def apply_upgrade(self):
        self.damage = 7
        self.block_val = 7
        self.description = "Gain 7 Block. Deal 7 damage."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg)

# ==========================================
# 7. NECROMANTIC EXHAUST & SOUL ENGINES
# ==========================================

class FeelNoPainCard(Card):
    def __init__(self):
        super().__init__("feel_no_pain", "Feel No Pain", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "Whenever a card is Exhausted, gain 3 Block.")
        self.block_gain = 3

    def apply_upgrade(self):
        self.block_gain = 4
        self.description = "Whenever a card is Exhausted, gain 4 Block."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("FeelNoPain", self.block_gain)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class DarkEmbraceCard(Card):
    def __init__(self):
        super().__init__("dark_embrace", "Dark Embrace", 2, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "Whenever a card is Exhausted, draw 1 card.")

    def apply_upgrade(self):
        self.cost = 1
        self.description = "Whenever a card is Exhausted, draw 1 card."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("DarkEmbrace", 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class CorruptionCard(Card):
    def __init__(self):
        super().__init__("corruption", "Corruption", 3, CardType.POWER, CardRarity.RARE,
                         TargetType.SELF, "Skills cost 0 Energy! Whenever you play a Skill, Exhaust it.")

    def apply_upgrade(self):
        self.cost = 2
        self.description = "Skills cost 0 Energy! Whenever you play a Skill, Exhaust it."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Corruption", 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class SecondWindCard(Card):
    def __init__(self):
        super().__init__("second_wind", "Second Wind", 1, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Exhaust all non-Attacks in hand. Gain 5 Block for each.")
        self.block_per = 5

    def apply_upgrade(self):
        self.block_per = 7
        self.description = "Exhaust all non-Attacks in hand. Gain 7 Block for each."

    def play(self, combat_state, player, target=None):
        non_attacks = [c for c in list(player.hand) if c.card_type != CardType.ATTACK and c != self]
        total_exhausted = len(non_attacks)
        for card in non_attacks:
            combat_state.exhaust_card(card)
        if total_exhausted > 0:
            blk = self.get_calculated_block(player, self.block_per * total_exhausted)
            player.gain_block(blk)
            combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class SeverSoulCard(Card):
    def __init__(self):
        super().__init__("sever_soul", "Sever Soul", 2, CardType.ATTACK, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Exhaust all non-Attacks in hand. Deal 16 damage.")
        self.damage = 16

    def apply_upgrade(self):
        self.damage = 22
        self.description = "Exhaust all non-Attacks in hand. Deal 22 damage."

    def play(self, combat_state, player, target=None):
        non_attacks = [c for c in list(player.hand) if c.card_type != CardType.ATTACK and c != self]
        for card in non_attacks:
            combat_state.exhaust_card(card)
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg, heavy=True)

class ExhumationCard(Card):
    def __init__(self):
        super().__init__("exhumation", "Exhumation", 1, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "Put a card from your Exhaust pile into your hand. Exhaust.", exhaust=True)

    def apply_upgrade(self):
        self.cost = 0
        self.description = "Put a card from your Exhaust pile into your hand. Exhaust."

    def play(self, combat_state, player, target=None):
        valid = [c for c in player.exhaust_pile if c.id_name != "exhumation" and c.card_type != CardType.POWER]
        if valid and len(player.hand) < player.max_hand_size:
            chosen = valid.pop()
            player.exhaust_pile.remove(chosen)
            player.hand.append(chosen)
            combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class DemonFormCard(Card):
    def __init__(self):
        super().__init__("demon_form", "Demon Form", 3, CardType.POWER, CardRarity.RARE,
                         TargetType.SELF, "At start of turn, gain 2 Strength.")
        self.strength = 2

    def apply_upgrade(self):
        self.strength = 3
        self.description = "At start of turn, gain 3 Strength."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("DemonForm", self.strength)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class FootworkCard(Card):
    def __init__(self):
        super().__init__("footwork", "Footwork", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "Gain 2 Dexterity.")
        self.dex = 2

    def apply_upgrade(self):
        self.dex = 3
        self.description = "Gain 3 Dexterity."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Dexterity", self.dex)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class CleaveCard(Card):
    def __init__(self):
        super().__init__("cleave", "Cleave", 1, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ALL_ENEMIES, "Deal 8 damage to ALL enemies.")
        self.damage = 8

    def apply_upgrade(self):
        self.damage = 11
        self.description = "Deal 11 damage to ALL enemies."

    def play(self, combat_state, player, target=None):
        dmg = self.get_calculated_damage(player, self.damage)
        for enemy in combat_state.enemies:
            if enemy.is_alive():
                combat_state.deal_attack_damage(player, enemy, dmg)


class NeutralizeCard(Card):
    def __init__(self):
        super().__init__("neutralize", "Neutralize", 0, CardType.ATTACK, CardRarity.STARTER,
                         TargetType.ENEMY, "Deal 3 damage. Apply 1 Weak.")
        self.damage = 3
        self.weak = 1

    def apply_upgrade(self):
        self.damage = 4
        self.weak = 2
        self.description = "Deal 4 damage. Apply 2 Weak."

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg)
            target.statuses.apply("Weak", self.weak)

class SoulDrainCard(Card):
    def __init__(self):
        super().__init__("soul_drain", "Soul Drain", 1, CardType.ATTACK, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Deal 8 damage. Heal 3 HP.")
        self.damage = 8
        self.heal_amt = 3

    def apply_upgrade(self):
        self.damage = 11
        self.heal_amt = 4
        self.description = "Deal 11 damage. Heal 4 HP."

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg)
            player.heal(self.heal_amt)

class LimitBreakCard(Card):
    def __init__(self):
        super().__init__("limit_break", "Limit Break", 1, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "Double your Strength. Exhaust.", exhaust=True)

    def apply_upgrade(self):
        self.exhaust = False
        self.description = "Double your Strength."

    def play(self, combat_state, player, target=None):
        curr_str = player.statuses.get("Strength")
        if curr_str > 0:
            player.statuses.apply("Strength", curr_str)
            combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class AngerCard(Card):
    def __init__(self, is_copy: bool = False):
        self.is_copy = is_copy
        desc = "Deal 6 damage. Exhaust. (Max 3/turn)" if is_copy else "Deal 6 damage. Add a copy to discard that Exhausts. (Max 3/turn)"
        super().__init__("anger", "Anger", 0, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, desc, exhaust=is_copy)
        self.damage = 6

    def apply_upgrade(self):
        self.damage = 8
        desc = "Deal 8 damage. Exhaust. (Max 3/turn)" if self.is_copy else "Deal 8 damage. Add a copy to discard that Exhausts. (Max 3/turn)"
        self.description = desc

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg)
            combat_state.anger_plays_this_turn += 1
            if not self.is_copy:
                copy_card = AngerCard(is_copy=True)
                if self.upgraded:
                    copy_card.upgrade()
                player.discard_pile.append(copy_card)

class WhirlwindCard(Card):
    def __init__(self):
        super().__init__("whirlwind", "Whirlwind", 2, CardType.ATTACK, CardRarity.UNCOMMON,
                         TargetType.ALL_ENEMIES, "Deal 5 damage to ALL enemies 3 times.")
        self.damage = 5
        self.hits = 3

    def apply_upgrade(self):
        self.damage = 7
        self.description = "Deal 7 damage to ALL enemies 3 times."

    def play(self, combat_state, player, target=None):
        dmg = self.get_calculated_damage(player, self.damage)
        for _ in range(self.hits):
            for enemy in combat_state.enemies:
                if enemy.is_alive():
                    combat_state.deal_attack_damage(player, enemy, dmg)

class TerrorCard(Card):
    def __init__(self):
        super().__init__("terror", "Terror", 0, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Apply 99 Vulnerable. Exhaust.", exhaust=True)

    def apply_upgrade(self):
        self.description = "Apply 99 Vulnerable."
        self.exhaust = False

    def play(self, combat_state, player, target=None):
        if target:
            target.statuses.apply("Vulnerable", 99)
            combat_state.spawn_debuff_fx(target.x + target.width // 2, target.y + target.height // 2)

class WraithFormCard(Card):
    def __init__(self):
        super().__init__("wraith_form", "Wraith Form", 3, CardType.POWER, CardRarity.RARE,
                         TargetType.SELF, "Gain 2 Intangible (reduce damage to 1).")
        self.turns = 2

    def apply_upgrade(self):
        self.turns = 3
        self.description = "Gain 3 Intangible (reduce damage to 1)."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Intangible", self.turns)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class AbyssalEchoCard(Card):
    def __init__(self):
        super().__init__("abyssal_echo", "Abyssal Echo", 3, CardType.POWER, CardRarity.RARE,
                         TargetType.SELF, "The first card played each turn is played twice.")

    def apply_upgrade(self):
        self.cost = 2
        self.description = "The first card played each turn is played twice."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("AbyssalEcho", 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class EnvenomCard(Card):
    def __init__(self):
        super().__init__("envenom", "Envenom", 2, CardType.POWER, CardRarity.RARE,
                         TargetType.SELF, "Whenever an Attack deals unblocked damage, apply 1 Poison.", exhaust=True)
        self.poison_amt = 1

    def apply_upgrade(self):
        self.poison_amt = 2
        self.description = "Whenever an Attack deals unblocked damage, apply 2 Poison."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Envenom", self.poison_amt)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class ChainLightningCard(Card):
    def __init__(self):
        super().__init__("chain_lightning", "Chain Lightning", 2, CardType.ATTACK, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Deal 14 damage. Deal 7 damage to all other enemies.")
        self.primary_dmg = 14
        self.splash_dmg = 7

    def apply_upgrade(self):
        self.primary_dmg = 18
        self.splash_dmg = 10
        self.description = "Deal 18 damage. Deal 10 damage to all other enemies."

    def play(self, combat_state, player, target=None):
        if target:
            p_dmg = self.get_calculated_damage(player, self.primary_dmg)
            combat_state.deal_attack_damage(player, target, p_dmg, heavy=True)
            s_dmg = self.get_calculated_damage(player, self.splash_dmg)
            for other in combat_state.enemies:
                if other.is_alive() and other != target:
                    combat_state.deal_attack_damage(player, other, s_dmg)

class ArmamentsCard(Card):
    def __init__(self):
        super().__init__("armaments", "Armaments", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 5 Block. Upgrade a card in hand for combat.")
        self.block_val = 5

    def apply_upgrade(self):
        self.block_val = 8
        self.description = "Gain 8 Block. Upgrade ALL cards in hand for combat."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)
        unupgraded = [c for c in player.hand if not c.upgraded and c != self]
        if self.upgraded:
            for c in unupgraded:
                c.upgrade()
        elif unupgraded:
            chosen = random.choice(unupgraded)
            chosen.upgrade()
            combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class FeedCard(Card):
    def __init__(self):
        super().__init__("feed", "Feed", 1, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ENEMY, "Deal 10 damage. Fatal: Permanently gain 3 Max HP.", exhaust=True)
        self.damage = 10
        self.hp_gain = 3

    def apply_upgrade(self):
        self.damage = 14
        self.hp_gain = 4
        self.description = "Deal 14 damage. Fatal: Permanently gain 4 Max HP."

    def play(self, combat_state, player, target=None):
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            hp_loss, _ = combat_state.deal_attack_damage(player, target, dmg, heavy=True)
            if not target.is_alive():
                player.max_hp += self.hp_gain
                player.hp += self.hp_gain
                combat_state.particle_mgr.spawn_popup(player.x + 40, player.y, f"+{self.hp_gain} MAX HP!", (255, 215, 0), is_crit=True)
                combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class FiendFireCard(Card):
    def __init__(self):
        super().__init__("fiend_fire", "Fiend Fire", 2, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ENEMY, "Exhaust ALL cards in hand. Deal 7 damage for each. Exhaust.", exhaust=True)
        self.dmg_per_card = 7

    def apply_upgrade(self):
        self.dmg_per_card = 10
        self.description = "Exhaust ALL cards in hand. Deal 10 damage for each. Exhaust."

    def play(self, combat_state, player, target=None):
        other_cards = [c for c in list(player.hand) if c != self]
        total_exhausted = len(other_cards)
        for c in other_cards:
            combat_state.exhaust_card(c)
        if target and total_exhausted > 0:
            for _ in range(total_exhausted):
                if target.is_alive():
                    dmg = self.get_calculated_damage(player, self.dmg_per_card)
                    combat_state.deal_attack_damage(player, target, dmg, heavy=True)

class SpotWeaknessCard(Card):
    def __init__(self):
        super().__init__("spot_weakness", "Spot Weakness", 1, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "If enemy intends to Attack, gain 3 Strength.")
        self.str_gain = 3

    def apply_upgrade(self):
        self.str_gain = 4
        self.description = "If enemy intends to Attack, gain 4 Strength."

    def play(self, combat_state, player, target=None):
        from models.enemy import IntentType
        if target and target.intent and target.intent.intent_type in (IntentType.ATTACK, IntentType.ATTACK_DEBUFF):
            player.statuses.apply("Strength", self.str_gain)
            combat_state.spawn_buff_fx(player.x + 60, player.y + 60)
            combat_state.particle_mgr.spawn_popup(player.x + 40, player.y, f"+{self.str_gain} Strength!", (255, 200, 80))

class ClashCard(Card):
    def __init__(self):
        super().__init__("clash", "Clash", 0, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, "Can only be played if all other cards in hand are Attacks. Deal 14 damage.")
        self.damage = 14

    def apply_upgrade(self):
        self.damage = 18
        self.description = "Can only be played if all other cards in hand are Attacks. Deal 18 damage."

    def play(self, combat_state, player, target=None):
        # Check if non-attacks exist in hand
        non_attacks = [c for c in player.hand if c != self and c.card_type != CardType.ATTACK]
        if non_attacks:
            combat_state.particle_mgr.spawn_popup(player.x + 40, player.y, "Only Attacks allowed!", (240, 60, 60))
            return
        if target:
            dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, dmg, heavy=True)

class TrueGritCard(Card):
    def __init__(self):
        super().__init__("true_grit", "True Grit", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 7 Block. Exhaust a random card in hand.")
        self.block_val = 7

    def apply_upgrade(self):
        self.block_val = 9
        self.description = "Gain 9 Block. Exhaust a random card in hand."

    def play(self, combat_state, player, target=None):
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)
        candidates = [c for c in player.hand if c != self]
        if candidates:
            to_exhaust = random.choice(candidates)
            combat_state.exhaust_card(to_exhaust)

class MalaiseCard(Card):
    def __init__(self):
        super().__init__("malaise", "Malaise", 1, CardType.SKILL, CardRarity.RARE,
                         TargetType.ENEMY, "Enemy loses 2 Strength and receives 2 Weak. Exhaust.", exhaust=True)
        self.power = 2

    def apply_upgrade(self):
        self.power = 3
        self.description = "Enemy loses 3 Strength and receives 3 Weak. Exhaust."

    def play(self, combat_state, player, target=None):
        if target:
            target.statuses.reduce("Strength", self.power)
            target.statuses.apply("Weak", self.power)
            combat_state.spawn_debuff_fx(target.x + target.width // 2, target.y + target.height // 2)

# ==========================================
# TEMPEST / LIGHTNING & FROST CARDS
# ==========================================

class ZapCard(Card):
    def __init__(self):
        super().__init__("zap", "Zap", 0, CardType.ATTACK, CardRarity.STARTER,
                         TargetType.ENEMY, "Deal 5 damage. Apply 1 Vulnerable.")
        self.damage = 5

    def apply_upgrade(self):
        self.damage = 8
        self.description = "Deal 8 damage. Apply 1 Vulnerable."

    def play(self, combat_state, player, target=None):
        if target:
            final_dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, final_dmg)
            target.statuses.apply("Vulnerable", 1)
            combat_state.spawn_debuff_fx(target.x + target.width // 2, target.y + target.height // 2)

class FrostBarrierCard(Card):
    def __init__(self):
        super().__init__("frost_barrier", "Frost Barrier", 1, CardType.SKILL, CardRarity.STARTER,
                         TargetType.SELF, "Gain 8 Block and 1 Dexterity.")
        self.block_val = 8

    def apply_upgrade(self):
        self.block_val = 11
        self.description = "Gain 11 Block and 1 Dexterity."

    def play(self, combat_state, player, target=None):
        player.gain_block(self.block_val)
        player.statuses.apply("Dexterity", 1)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class ThunderStrikeCard(Card):
    def __init__(self):
        super().__init__("thunder_strike", "Thunder Strike", 1, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, "Deal 9 damage. If target has Vulnerable, refund 1 Energy.")
        self.damage = 9

    def apply_upgrade(self):
        self.damage = 13
        self.description = "Deal 13 damage. If target has Vulnerable, refund 1 Energy."

    def play(self, combat_state, player, target=None):
        if target:
            is_vuln = target.statuses.has("Vulnerable")
            final_dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, final_dmg, heavy=True)
            if is_vuln:
                player.energy += 1
                combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class StaticDischargeCard(Card):
    def __init__(self):
        super().__init__("static_discharge", "Static Discharge", 1, CardType.POWER, CardRarity.UNCOMMON,
                         TargetType.SELF, "Power: Gain 4 Thorns and 1 Strength.")
        self.power = 4

    def apply_upgrade(self):
        self.power = 6
        self.description = "Power: Gain 6 Thorns and 2 Strength."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("Thorns", self.power)
        player.statuses.apply("Strength", 2 if self.upgraded else 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class BallLightningCard(Card):
    def __init__(self):
        super().__init__("ball_lightning", "Ball Lightning", 1, CardType.ATTACK, CardRarity.COMMON,
                         TargetType.ENEMY, "Deal 8 damage. Apply 2 Vulnerable.")
        self.damage = 8

    def apply_upgrade(self):
        self.damage = 11
        self.description = "Deal 11 damage. Apply 2 Vulnerable."

    def play(self, combat_state, player, target=None):
        if target:
            final_dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, final_dmg)
            target.statuses.apply("Vulnerable", 2)
            combat_state.spawn_debuff_fx(target.x + target.width // 2, target.y + target.height // 2)

class GlacierCard(Card):
    def __init__(self):
        super().__init__("glacier", "Glacier", 2, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Gain 15 Block. Apply 2 Weak to ALL enemies.")
        self.block_val = 15

    def apply_upgrade(self):
        self.block_val = 20
        self.description = "Gain 20 Block. Apply 2 Weak to ALL enemies."

    def play(self, combat_state, player, target=None):
        player.gain_block(self.block_val)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)
        for e in combat_state.enemies:
            if e.is_alive():
                e.statuses.apply("Weak", 2)
                combat_state.spawn_debuff_fx(e.x + e.width // 2, e.y + e.height // 2)

class BlizzardCard(Card):
    def __init__(self):
        super().__init__("blizzard", "Blizzard", 1, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ALL_ENEMIES, "Deal damage to ALL enemies equal to your current Block.")

    def apply_upgrade(self):
        self.cost = 0
        self.description = "(0 Energy) Deal damage to ALL enemies equal to your current Block."

    def play(self, combat_state, player, target=None):
        dmg = player.block
        for e in combat_state.enemies:
            if e.is_alive():
                final_dmg = self.get_calculated_damage(player, dmg)
                combat_state.deal_attack_damage(player, e, final_dmg, heavy=True)

class SuperconductorCard(Card):
    def __init__(self):
        super().__init__("superconductor", "Superconductor", 0, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Gain 2 Energy. Take 3 self-damage. Exhaust.", exhaust=True)

    def apply_upgrade(self):
        self.description = "Gain 3 Energy. Take 3 self-damage. Exhaust."

    def play(self, combat_state, player, target=None):
        player.energy += 3 if self.upgraded else 2
        combat_state.player_take_card_damage(3)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

# ==========================================
# RADIANT TEMPLAR / HOLY CARDS
# ==========================================

class SmiteCard(Card):
    def __init__(self):
        super().__init__("smite", "Smite", 1, CardType.ATTACK, CardRarity.STARTER,
                         TargetType.ENEMY, "Deal 10 Holy damage. Gain 2 Thorns.")
        self.damage = 10

    def apply_upgrade(self):
        self.damage = 14
        self.description = "Deal 14 Holy damage. Gain 3 Thorns."

    def play(self, combat_state, player, target=None):
        if target:
            final_dmg = self.get_calculated_damage(player, self.damage)
            combat_state.deal_attack_damage(player, target, final_dmg, heavy=True)
            player.statuses.apply("Thorns", 3 if self.upgraded else 2)
            combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class HolyShieldCard(Card):
    def __init__(self):
        super().__init__("holy_shield", "Holy Shield", 1, CardType.SKILL, CardRarity.STARTER,
                         TargetType.SELF, "Gain 8 Block and 2 Thorns.")
        self.block_val = 8

    def apply_upgrade(self):
        self.block_val = 11
        self.description = "Gain 11 Block and 3 Thorns."

    def play(self, combat_state, player, target=None):
        player.gain_block(self.block_val)
        player.statuses.apply("Thorns", 3 if self.upgraded else 2)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class ConsecrationCard(Card):
    def __init__(self):
        super().__init__("consecration", "Consecration", 1, CardType.ATTACK, CardRarity.STARTER,
                         TargetType.ALL_ENEMIES, "Deal 8 Holy damage to ALL enemies.")
        self.damage = 8

    def apply_upgrade(self):
        self.damage = 12
        self.description = "Deal 12 Holy damage to ALL enemies."

    def play(self, combat_state, player, target=None):
        for e in combat_state.enemies:
            if e.is_alive():
                final_dmg = self.get_calculated_damage(player, self.damage)
                combat_state.deal_attack_damage(player, e, final_dmg)

class RadiantVowCard(Card):
    def __init__(self):
        super().__init__("radiant_vow", "Radiant Vow", 1, CardType.SKILL, CardRarity.COMMON,
                         TargetType.SELF, "Gain 6 Block. Your next Attack deals double damage.")
        self.block_val = 6

    def apply_upgrade(self):
        self.block_val = 9
        self.description = "Gain 9 Block. Your next Attack deals double damage."

    def play(self, combat_state, player, target=None):
        player.gain_block(self.block_val)
        player.statuses.apply("DoubleTap", 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class HeavensFuryCard(Card):
    def __init__(self):
        super().__init__("heavens_fury", "Heaven's Fury", 2, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ENEMY, "Deal 18 damage. If this kills the enemy, heal 8 HP.")
        self.damage = 18

    def apply_upgrade(self):
        self.damage = 24
        self.description = "Deal 24 damage. If this kills the enemy, heal 12 HP."

    def play(self, combat_state, player, target=None):
        if target:
            final_dmg = self.get_calculated_damage(player, self.damage)
            hp_loss, _ = combat_state.deal_attack_damage(player, target, final_dmg, heavy=True)
            if not target.is_alive():
                player.heal(12 if self.upgraded else 8)
                combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class DivineFavorCard(Card):
    def __init__(self):
        super().__init__("divine_favor", "Divine Favor", 1, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.SELF, "Draw 2 cards and gain 5 Block.")
        self.block_val = 5

    def apply_upgrade(self):
        self.block_val = 8
        self.description = "Draw 2 cards and gain 8 Block."

    def play(self, combat_state, player, target=None):
        player.draw_cards(2)
        blk = self.get_calculated_block(player, self.block_val)
        player.gain_block(blk)
        combat_state.spawn_block_fx(player.x + 60, player.y + 70)

class JudgmentCard(Card):
    def __init__(self):
        super().__init__("judgment", "Judgment", 1, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ENEMY, "If enemy has 25 or less HP, instantly smite them. Otherwise 8 damage.", exhaust=True)

    def apply_upgrade(self):
        self.description = "If enemy has 35 or less HP, instantly smite them. Otherwise 12 damage."

    def play(self, combat_state, player, target=None):
        if target:
            threshold = 35 if self.upgraded else 25
            if target.hp <= threshold:
                target.take_damage(999, is_attack=False)
                from engine.sound import play_sfx
                play_sfx('heavy_hit', 1.0)
                combat_state.screen_shake.start(intensity=12.0, duration=0.4)
                combat_state.particle_mgr.spawn_burst(target.x + target.width // 2, target.y + target.height // 2, (255, 230, 80), count=40, speed=8.0)
            else:
                dmg = self.get_calculated_damage(player, 12 if self.upgraded else 8)
                combat_state.deal_attack_damage(player, target, dmg)

# ==========================================
# UNIVERSAL POWER & HIGH-COMBO CARDS
# ==========================================

class ApotheosisCard(Card):
    def __init__(self):
        super().__init__("apotheosis", "Apotheosis", 2, CardType.SKILL, CardRarity.RARE,
                         TargetType.SELF, "Upgrade ALL cards in your hand and draw pile for combat. Exhaust.", exhaust=True)

    def apply_upgrade(self):
        self.cost = 1
        self.description = "(1 Energy) Upgrade ALL cards in hand and draw pile for combat. Exhaust."

    def play(self, combat_state, player, target=None):
        for c in player.hand + player.draw_pile + player.discard_pile:
            if not c.upgraded:
                c.upgrade()
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class EchoFormCard(Card):
    def __init__(self):
        super().__init__("echo_form", "Echo Form", 3, CardType.POWER, CardRarity.RARE,
                         TargetType.SELF, "Power: The first Attack and first Skill you play each turn play twice.")

    def apply_upgrade(self):
        self.cost = 2
        self.description = "(2 Energy) Power: The first Attack and first Skill you play each turn play twice."

    def play(self, combat_state, player, target=None):
        player.statuses.apply("DoubleTap", 1)
        player.statuses.apply("Burst", 1)
        combat_state.spawn_buff_fx(player.x + 60, player.y + 60)

class OmnislashCard(Card):
    def __init__(self):
        super().__init__("omnislash", "Omnislash", 2, CardType.ATTACK, CardRarity.RARE,
                         TargetType.ALL_ENEMIES, "Deal 6 damage 5 times to random enemies.")
        self.hits = 5

    def apply_upgrade(self):
        self.hits = 7
        self.description = "Deal 6 damage 7 times to random enemies."

    def play(self, combat_state, player, target=None):
        for _ in range(self.hits):
            alive = [e for e in combat_state.enemies if e.is_alive()]
            if not alive:
                break
            chosen = random.choice(alive)
            dmg = self.get_calculated_damage(player, 6)
            combat_state.deal_attack_damage(player, chosen, dmg)

class DarkShacklesCard(Card):
    def __init__(self):
        super().__init__("dark_shackles", "Dark Shackles", 0, CardType.SKILL, CardRarity.UNCOMMON,
                         TargetType.ENEMY, "Target loses 5 Strength and gains 2 Weak. Exhaust.", exhaust=True)

    def apply_upgrade(self):
        self.description = "Target loses 8 Strength and gains 3 Weak. Exhaust."

    def play(self, combat_state, player, target=None):
        if target:
            target.statuses.reduce("Strength", 8 if self.upgraded else 5)
            target.statuses.apply("Weak", 3 if self.upgraded else 2)
            combat_state.spawn_debuff_fx(target.x + target.width // 2, target.y + target.height // 2)

ALL_CARD_CLASSES = [
    # 0-cost & buffs
    AdrenalineCard, FlexCard, BattleTranceCard, SeeingRedCard,
    WarcryCard, ShadowstepCard, GougeCard, OfferingCard,
    NeutralizeCard, TerrorCard, AngerCard, ClashCard,
    SuperconductorCard, DarkShacklesCard, DivineFavorCard,
    # Blood & berserker
    HemokinesisCard, RuptureCard, CombustionCard, BloodForBloodCard,
    HeavyBladeCard, ReaperCard, BashCard, LimitBreakCard, WhirlwindCard,
    FeedCard, FiendFireCard, SpotWeaknessCard, TrueGritCard, ArmamentsCard,
    # Shivs & tempo
    BladeDanceCard, CloakAndDaggerCard, AccuracyCard, InfiniteBladesCard,
    StormOfSteelCard, FinisherCard, DoubleTapCard, BurstCard, BackflipCard,
    # Poison
    DeadlyPoisonCard, BouncingFlaskCard, CripplingCloudCard,
    CorpseExplosionCard, CatalystCard, NoxiousFumesCard, EnvenomCard, MalaiseCard,
    # Block & Fortress
    DefendCard, IronWaveCard, BodySlamCard, EntrenchCard,
    FlameBarrierCard, BarricadeCard, ImperviousCard,
    # Necromancy, Exhaust & Arcane
    FeelNoPainCard, DarkEmbraceCard, CorruptionCard, SecondWindCard,
    SeverSoulCard, ExhumationCard, DemonFormCard, FootworkCard, CleaveCard,
    SoulDrainCard, WraithFormCard, AbyssalEchoCard, ChainLightningCard,
    # Tempest & Lightning
    ZapCard, FrostBarrierCard, ThunderStrikeCard, StaticDischargeCard,
    BallLightningCard, GlacierCard, BlizzardCard,
    # Radiant Templar & Holy
    SmiteCard, HolyShieldCard, ConsecrationCard, RadiantVowCard,
    HeavensFuryCard, JudgmentCard,
    # Legendary Powers
    ApotheosisCard, EchoFormCard, OmnislashCard
]

CHARACTER_CARD_MAPPINGS = {
    "blood_knight": [
        BashCard, IronWaveCard, FlexCard, CleaveCard, BattleTranceCard,
        HeavyBladeCard, LimitBreakCard, WhirlwindCard, FeedCard, FiendFireCard,
        SpotWeaknessCard, TrueGritCard, ArmamentsCard, BodySlamCard, EntrenchCard,
        FlameBarrierCard, BarricadeCard, ImperviousCard, DemonFormCard, ClashCard
    ],
    "shadow_assassin": [
        NeutralizeCard, DeadlyPoisonCard, BladeDanceCard, ShadowstepCard, GougeCard,
        TerrorCard, CloakAndDaggerCard, AccuracyCard, InfiniteBladesCard, StormOfSteelCard,
        FinisherCard, DoubleTapCard, BurstCard, BackflipCard, BouncingFlaskCard,
        CripplingCloudCard, CatalystCard, NoxiousFumesCard, EnvenomCard, MalaiseCard,
        FootworkCard, WraithFormCard
    ],
    "void_necromancer": [
        SoulDrainCard, OfferingCard, CorpseExplosionCard, WarcryCard, HemokinesisCard,
        RuptureCard, CombustionCard, BloodForBloodCard, ReaperCard, FeelNoPainCard,
        DarkEmbraceCard, CorruptionCard, SecondWindCard, SeverSoulCard, ExhumationCard,
        AbyssalEchoCard
    ],
    "tempest_herald": [
        ZapCard, FrostBarrierCard, ThunderStrikeCard, StaticDischargeCard,
        BallLightningCard, GlacierCard, BlizzardCard, ChainLightningCard, SuperconductorCard
    ],
    "radiant_templar": [
        SmiteCard, HolyShieldCard, ConsecrationCard, RadiantVowCard,
        HeavensFuryCard, JudgmentCard, DivineFavorCard
    ]
}

for char_id, card_classes in CHARACTER_CARD_MAPPINGS.items():
    for cls in card_classes:
        cls.character = char_id

def get_cards_for_character(char_id: str | None = None) -> list[type[Card]]:
    """Returns card classes available to the specified character (exclusive cards + neutral cards)."""
    if not char_id:
        return list(ALL_CARD_CLASSES)
    return [cls for cls in ALL_CARD_CLASSES if getattr(cls, 'character', None) in (None, char_id)]

def get_starter_deck():
    """Default starter deck fallback."""
    deck = []
    for _ in range(4):
        deck.append(StrikeCard())
    for _ in range(4):
        deck.append(DefendCard())
    deck.append(BashCard())
    deck.append(IronWaveCard())
    deck.append(FlexCard())
    deck.append(ShadowstepCard())
    return deck
