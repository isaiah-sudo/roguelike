"""
Status effects system for players and enemies.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class StatusEffect:
    name: str
    amount: int
    description: str
    is_debuff: bool

STATUS_METADATA = {
    "Vulnerable": ("Vulnerable", True, "Takes 50% more damage from attacks."),
    "Weak": ("Weak", True, "Deals 25% less damage with attacks."),
    "Strength": ("Strength", False, "Attacks deal additional damage."),
    "Dexterity": ("Dexterity", False, "Gain additional Block from cards."),
    "Poison": ("Poison", True, "Takes damage equal to Poison stacks at turn end, then loses 1 stack."),
    "Thorns": ("Thorns", False, "Deals damage to attacker when hit by an attack."),
    "Metallicize": ("Metallicize", False, "Gain Block at end of turn."),
    "Ritual": ("Ritual", False, "Gain Strength at end of turn."),
    "Artifact": ("Artifact", False, "Negates the next debuff applied."),
    "Barricade": ("Barricade", False, "Block is not removed at the start of your turn."),
    "Rupture": ("Rupture", False, "Whenever you lose HP from a card, gain Strength."),
    "Combustion": ("Combustion", False, "At end of turn, lose 1 HP and deal damage to ALL enemies."),
    "DoubleTap": ("Double Tap", False, "Your next Attack is played twice."),
    "Burst": ("Burst", False, "Your next Skill is played twice."),
    "Accuracy": ("Accuracy", False, "Shivs deal additional damage."),
    "FeelNoPain": ("Feel No Pain", False, "Whenever a card is Exhausted, gain Block."),
    "DarkEmbrace": ("Dark Embrace", False, "Whenever a card is Exhausted, draw 1 card."),
    "Corruption": ("Corruption", False, "Skills cost 0 Energy and Exhaust when played."),
    "FlameBarrier": ("Flame Barrier", False, "When attacked this turn, deal damage back to attacker."),
    "FlexStrength": ("Flex", False, "Strength lost at the end of this turn."),
    "CorpseExplosion": ("Corpse Explosion", True, "On death, explodes dealing Max HP damage to all surviving enemies."),
    "InfiniteBlades": ("Infinite Blades", False, "At start of turn, add 1 Shiv to hand."),
    "NoxiousFumes": ("Noxious Fumes", False, "At start of turn, apply Poison to ALL enemies."),
    "DemonForm": ("Demon Form", False, "At start of turn, gain Strength."),
    "Intangible": ("Intangible", False, "All damage taken is reduced to 1."),
    "Rage": ("Rage", False, "Whenever you take damage, gain Strength."),
    "AbyssalEcho": ("Abyssal Echo", False, "The first card played each turn is played twice.")
}

class StatusManager:
    def __init__(self, owner=None):
        self.statuses: Dict[str, int] = {}
        self.owner = owner

    def get(self, name: str) -> int:
        return self.statuses.get(name, 0)

    def apply(self, name: str, amount: int) -> bool:
        if amount <= 0:
            return False

        meta = STATUS_METADATA.get(name)
        is_debuff = meta[1] if meta else False

        # Check Artifact block for debuffs
        if is_debuff and self.get("Artifact") > 0:
            self.statuses["Artifact"] -= 1
            if self.statuses["Artifact"] <= 0:
                del self.statuses["Artifact"]
            return False  # Debuff blocked

        # Radiant Templar Thorns cannot stack
        if name == "Thorns" and getattr(self.owner, 'char_id', None) == 'radiant_templar':
            if self.get("Thorns") <= 0:
                self.statuses["Thorns"] = amount
            else:
                self.statuses["Thorns"] = max(self.statuses["Thorns"], amount)
            return True

        self.statuses[name] = self.statuses.get(name, 0) + amount
        return True

    def reduce(self, name: str, amount: int = 1):
        if name in self.statuses:
            self.statuses[name] -= amount
            if self.statuses[name] <= 0:
                del self.statuses[name]

    def clear(self):
        self.statuses.clear()

    def has(self, name: str) -> bool:
        return self.statuses.get(name, 0) > 0
