"""
Combatant base class for Player and Enemies.
"""
from models.status import StatusManager

class Entity:
    def __init__(self, name: str, max_hp: int):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.block = 0
        self.statuses = StatusManager(owner=self)
        
        # Visual state
        self.x = 0
        self.y = 0
        self.width = 120
        self.height = 140
        self.flash_timer = 0.0
        self.lunge_x = 0.0
        self.target_lunge_x = 0.0

    def update(self, dt):
        self.flash_timer = max(0.0, self.flash_timer - dt)
        # Smooth interpolation towards target lunge offset
        self.lunge_x += (self.target_lunge_x - self.lunge_x) * min(1.0, dt * 14.0)
        # Gradually relax lunge back to 0
        if abs(self.target_lunge_x) > 0.1:
            self.target_lunge_x += (0.0 - self.target_lunge_x) * min(1.0, dt * 6.0)

    def is_alive(self) -> bool:
        return self.hp > 0

    def gain_block(self, amount: int):
        if amount <= 0:
            return
        dex = self.statuses.get("Dexterity")
        final_block = max(0, amount + dex)
        self.block += final_block
        return final_block

    def take_damage(self, raw_damage: int, is_attack: bool = True) -> tuple[int, int]:
        """
        Takes damage, accounting for Vulnerable and Block.
        Returns: (hp_damage, block_absorbed)
        """
        damage = raw_damage
        if is_attack and self.statuses.get("Vulnerable") > 0:
            damage = int(damage * 1.5)

        if self.statuses.get("Intangible") > 0:
            damage = min(1, damage)

        block_absorbed = min(self.block, damage)
        self.block -= block_absorbed
        hp_damage = damage - block_absorbed

        self.hp = max(0, self.hp - hp_damage)
        self.flash_timer = 0.2
        return hp_damage, block_absorbed

    def heal(self, amount: int) -> int:
        if amount <= 0:
            return 0
        prev_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - prev_hp

    def start_turn(self):
        # Reset block unless entity has Barricade
        if not self.statuses.has("Barricade"):
            self.block = 0

    def end_turn(self):
        # Trigger Metallicize
        metal = self.statuses.get("Metallicize")
        if metal > 0:
            self.gain_block(metal)

        # Trigger Ritual
        ritual = self.statuses.get("Ritual")
        if ritual > 0:
            self.statuses.apply("Strength", ritual)

        # Remove temporary Flex Strength
        flex = self.statuses.get("FlexStrength")
        if flex > 0:
            self.statuses.reduce("Strength", flex)
            self.statuses.reduce("FlexStrength", flex)

        # Flame Barrier expires at end of turn
        if self.statuses.has("FlameBarrier"):
            self.statuses.clear_status("FlameBarrier") if hasattr(self.statuses, "clear_status") else self.statuses.reduce("FlameBarrier", self.statuses.get("FlameBarrier"))

        # Decrement turn-based debuffs and buffs
        if self.statuses.get("Vulnerable") > 0:
            self.statuses.reduce("Vulnerable", 1)
        if self.statuses.get("Weak") > 0:
            self.statuses.reduce("Weak", 1)
        if self.statuses.get("Intangible") > 0:
            self.statuses.reduce("Intangible", 1)
