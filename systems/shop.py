"""
Merchant / Shop System: buy cards, relics, potions, and remove unwanted cards.
"""
import random
from models.card import ALL_CARD_CLASSES, Card
from models.relic import ALL_RELIC_CLASSES, Relic
from models.potion import ALL_POTIONS, Potion
from engine.sound import play_sfx

class ShopItem:
    def __init__(self, item, cost: int):
        self.item = item
        self.cost = cost
        self.purchased = False

class Shop:
    def __init__(self):
        self.cards: list[ShopItem] = []
        self.relics: list[ShopItem] = []
        self.potions: list[ShopItem] = []
        self.card_removal_cost = 75
        self.removal_used = False
        self.generate_inventory()

    def generate_inventory(self):
        # 5 Cards
        selected_classes = random.sample(ALL_CARD_CLASSES, min(5, len(ALL_CARD_CLASSES)))
        for cls in selected_classes:
            card = cls()
            cost = random.randint(45, 80)
            self.cards.append(ShopItem(card, cost))

        # 2 Relics
        selected_relics = random.sample(ALL_RELIC_CLASSES, min(2, len(ALL_RELIC_CLASSES)))
        for r_cls in selected_relics:
            relic = r_cls()
            cost = random.randint(140, 210)
            self.relics.append(ShopItem(relic, cost))

        # 2 Potions
        selected_pots = random.sample(ALL_POTIONS, min(2, len(ALL_POTIONS)))
        for p_cls in selected_pots:
            pot = p_cls()
            cost = random.randint(40, 65)
            self.potions.append(ShopItem(pot, cost))

    def buy_card(self, player, shop_item: ShopItem) -> bool:
        if shop_item.purchased or player.gold < shop_item.cost:
            return False
        player.gold -= shop_item.cost
        shop_item.purchased = True
        player.deck.append(shop_item.item)
        play_sfx('gold', 0.6)
        return True

    def buy_relic(self, player, shop_item: ShopItem) -> bool:
        if shop_item.purchased or player.gold < shop_item.cost:
            return False
        player.gold -= shop_item.cost
        shop_item.purchased = True
        player.add_relic(shop_item.item)
        play_sfx('gold', 0.6)
        return True

    def buy_potion(self, player, shop_item: ShopItem) -> bool:
        if shop_item.purchased or player.gold < shop_item.cost:
            return False
        empty_slot = -1
        for i, p in enumerate(player.potions):
            if p is None:
                empty_slot = i
                break
        if empty_slot == -1:
            return False  # Slots full

        player.gold -= shop_item.cost
        shop_item.purchased = True
        player.potions[empty_slot] = shop_item.item
        play_sfx('gold', 0.6)
        return True

    def remove_card(self, player, card: Card) -> bool:
        if self.removal_used or player.gold < self.card_removal_cost:
            return False
        if card in player.deck:
            player.deck.remove(card)
            player.gold -= self.card_removal_cost
            self.removal_used = True
            self.card_removal_cost += 25
            play_sfx('card_draw', 0.6)
            return True
        return False
