"""
Dark fantasy narrative mystery events.
"""
import random
from models.relic import ALL_RELIC_CLASSES
from models.potion import ALL_POTIONS
from engine.sound import play_sfx

class GameEvent:
    def __init__(self, title: str, story: str, options: list[tuple[str, callable]]):
        self.title = title
        self.story = story
        self.options = options  # list of (option_text, resolution_func)
        self.resolved = False
        self.result_text = ""

def generate_random_event(player) -> GameEvent:
    events = [
        _create_blood_altar(player),
        _create_ghostly_smith(player),
        _create_cursed_coffers(player),
        _create_wandering_witch(player)
    ]
    return random.choice(events)

def _create_blood_altar(player) -> GameEvent:
    def sacrifice(p):
        p.hp = max(1, p.hp - 10)
        relic = random.choice(ALL_RELIC_CLASSES)()
        p.add_relic(relic)
        play_sfx('debuff', 0.6)
        return f"You bleed upon the ancient obsidian altar (-10 HP). The shadows coalesce into a {relic.name}!"

    def pray(p):
        p.heal(8)
        play_sfx('buff', 0.6)
        return "You whisper a quiet prayer for safety. A gentle warmth restores 8 HP."

    return GameEvent(
        "The Blood Altar",
        "Deep within the cold catacombs, you come upon a sinister altar carved from glistening obsidian. Whispers echo through the chamber, demanding a tribute of vital blood.",
        [
            ("Sacrifice 10 HP to claim an ancient Relic", sacrifice),
            ("Pray quietly and recover 8 HP", pray),
            ("Leave without touching anything", lambda p: "You step away into the dark corridors.")
        ]
    )

def _create_ghostly_smith(player) -> GameEvent:
    def upgrade_card(p):
        unupgraded = [c for c in p.deck if not c.upgraded]
        if unupgraded:
            target = random.choice(unupgraded)
            target.upgrade()
            play_sfx('buff', 0.6)
            return f"The phantom spirit strikes his ethereal hammer. {target.name} has been upgraded!"
        return "Your deck is already fully mastered."

    def strengthen_vitality(p):
        p.max_hp += 8
        p.hp += 8
        play_sfx('buff', 0.6)
        return "The smith tempers your resolve. Your Max HP increased by 8!"

    return GameEvent(
        "The Ghostly Blacksmith",
        "An ethereal specter hammering away at an iron anvil manifests before you. He turns hollow, sorrowful eyes toward you, offering the services of the forgotten forge.",
        [
            ("Forge your weapons (Upgrade a random card)", upgrade_card),
            ("Reinforce your vitality (+8 Max HP)", strengthen_vitality),
            ("Leave quietly", lambda p: "You nod in respect and continue your journey.")
        ]
    )

def _create_cursed_coffers(player) -> GameEvent:
    def take_gold(p):
        p.gold += 125
        p.hp = max(1, p.hp - 12)
        play_sfx('gold', 0.6)
        play_sfx('debuff', 0.6)
        return "The chest violently snaps shut on your arm as dark miasma burns you (-12 HP), but you haul away 125 Gold!"

    return GameEvent(
        "The Cursed Sarcophagus",
        "A gilded tomb decorated with skull reliefs rests half-open. Inside, piles of gold coins sparkle enticingly under a shroud of writhing black smoke.",
        [
            ("Plunder the gold (Take 12 damage, Gain 125 Gold)", take_gold),
            ("Do not tempt fate (Leave)", lambda p: "Wisdom prevails; you leave the cursed gold undisturbed.")
        ]
    )

def _create_wandering_witch(player) -> GameEvent:
    def drink_brew(p):
        p.heal(22)
        pot = random.choice(ALL_POTIONS)()
        # Add potion
        for i in range(len(p.potions)):
            if p.potions[i] is None:
                p.potions[i] = pot
                break
        play_sfx('buff', 0.6)
        return f"The dark brew burns your throat but invigorates your blood (+22 HP). She hands you a {pot.name}!"

    return GameEvent(
        "The Wandering Witch",
        "A cloaked witch sitting by a cauldron of bubbling purple broth invites you to sit. 'A sip of my vintage brew will mend your wounds, wanderer,' she cackles.",
        [
            ("Drink the dark concoction (Heal 22 HP, Receive a potion)", drink_brew),
            ("Politely decline", lambda p: "You decline her offer and vanish into the catacombs.")
        ]
    )
