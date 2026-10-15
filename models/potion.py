"""
Consumable potions usable during combat.
"""
from typing import Optional

class Potion:
    def __init__(self, id_name: str, name: str, description: str, color: tuple, target_required: bool = False):
        self.id_name = id_name
        self.name = name
        self.description = description
        self.color = color
        self.target_required = target_required

    def use(self, combat_state, player, target=None):
        raise NotImplementedError

class HealthPotion(Potion):
    def __init__(self):
        super().__init__("health_pot", "Blood Flask", "Heal 20 HP.", (210, 45, 60))

    def use(self, combat_state, player, target=None):
        player.heal(20)

class BlockPotion(Potion):
    def __init__(self):
        super().__init__("block_pot", "Iron Brew", "Gain 15 Block.", (60, 140, 240))

    def use(self, combat_state, player, target=None):
        player.gain_block(15)

class StrengthPotion(Potion):
    def __init__(self):
        super().__init__("str_pot", "Wrath Draught", "Gain 2 Strength.", (240, 120, 40))

    def use(self, combat_state, player, target=None):
        player.statuses.apply("Strength", 2)

class PoisonPotion(Potion):
    def __init__(self):
        super().__init__("poison_pot", "Viper Toxin", "Apply 6 Poison to target.", (70, 210, 90), target_required=True)

    def use(self, combat_state, player, target=None):
        if target:
            target.statuses.apply("Poison", 6)

class EnergyPotion(Potion):
    def __init__(self):
        super().__init__("energy_pot", "Starlight Nectar", "Gain 2 Energy.", (245, 230, 90))

    def use(self, combat_state, player, target=None):
        player.energy += 2

ALL_POTIONS = [HealthPotion, BlockPotion, StrengthPotion, PoisonPotion, EnergyPotion]
