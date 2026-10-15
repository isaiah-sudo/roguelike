"""
Combat Rewards: Card Drafting, Gold, Potions, and Relics.
Includes 3-choice Boss Relic Draft upon defeating Act Bosses.
"""
import random
from models.card import ALL_CARD_CLASSES, Card, CardRarity
from models.potion import ALL_POTIONS
from models.relic import ALL_RELIC_CLASSES, BOSS_RELIC_CLASSES, Relic
from engine.sound import play_sfx

class CombatReward:
    def __init__(self, is_elite: bool = False, is_boss: bool = False, act: int = 1):
        self.is_elite = is_elite
        self.is_boss = is_boss
        self.act = act
        
        # Gold
        base_gold = random.randint(15, 25)
        if is_elite:
            base_gold = random.randint(35, 55)
        elif is_boss:
            base_gold = random.randint(110, 150)
        self.gold = base_gold

        # Card rewards (Draft 3 cards)
        self.card_options: list[Card] = []
        if is_boss:
            # Boss rewards: guaranteed high-tier rare & uncommon cards, all upgraded!
            rare_pool = [c for c in ALL_CARD_CLASSES if getattr(c(), 'rarity', None) in (CardRarity.RARE, CardRarity.UNCOMMON)]
            selected_classes = random.sample(rare_pool if len(rare_pool) >= 3 else ALL_CARD_CLASSES, 3)
            for cls in selected_classes:
                card = cls()
                card.upgrade()
                self.card_options.append(card)
        else:
            selected_classes = random.sample(ALL_CARD_CLASSES, min(3, len(ALL_CARD_CLASSES)))
            for cls in selected_classes:
                card = cls()
                if random.random() < (0.35 if is_elite else 0.12):
                    card.upgrade()
                self.card_options.append(card)

        # Boss Relic Draft (Choose 1 of 3 Boss Relics)
        self.boss_relic_options: list[Relic] = []
        self.boss_relic_claimed = False
        if is_boss:
            chosen_classes = random.sample(BOSS_RELIC_CLASSES, min(3, len(BOSS_RELIC_CLASSES)))
            self.boss_relic_options = [cls() for cls in chosen_classes]

        # Regular Relic reward (guaranteed for Elite)
        self.relic_reward = None
        if is_elite or (not is_boss and random.random() < 0.15):
            relic_cls = random.choice(ALL_RELIC_CLASSES)
            self.relic_reward = relic_cls()

        # Potion reward
        self.potion_reward = None
        if is_boss or random.random() < 0.45:
            pot_cls = random.choice(ALL_POTIONS)
            self.potion_reward = pot_cls()

        self.gold_claimed = False
        self.card_claimed = False
        self.relic_claimed = False
        self.potion_claimed = False

    def claim_gold(self, player):
        if not self.gold_claimed:
            player.gold += self.gold
            self.gold_claimed = True
            play_sfx('gold', 0.6)

    def choose_card(self, player, card: Card):
        if not self.card_claimed:
            player.deck.append(card)
            self.card_claimed = True
            play_sfx('card_draw', 0.6)

    def choose_boss_relic(self, player, relic: Relic):
        if not self.boss_relic_claimed:
            player.add_relic(relic)
            if hasattr(relic, "on_pickup"):
                relic.on_pickup(player)
            self.boss_relic_claimed = True
            play_sfx('buff', 0.8)

    def claim_relic(self, player):
        if self.relic_reward and not self.relic_claimed:
            player.add_relic(self.relic_reward)
            if hasattr(self.relic_reward, "on_pickup"):
                self.relic_reward.on_pickup(player)
            self.relic_claimed = True
            play_sfx('buff', 0.6)

            # Black Star synergy: claim extra relic on Elite defeat
            if self.is_elite and player.has_relic("black_star"):
                extra_cls = random.choice(ALL_RELIC_CLASSES)
                extra_relic = extra_cls()
                player.add_relic(extra_relic)
                if hasattr(extra_relic, "on_pickup"):
                    extra_relic.on_pickup(player)

    def claim_potion(self, player):
        if self.potion_reward and not self.potion_claimed:
            for i in range(len(player.potions)):
                if player.potions[i] is None:
                    player.potions[i] = self.potion_reward
                    self.potion_claimed = True
                    play_sfx('buff', 0.5)
                    break

