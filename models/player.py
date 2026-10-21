"""
Player class and Character Classes (Blood Knight, Shadow Assassin, Void Necromancer).
Each character has a unique starter deck, starter relic, stats, and visual avatar.
"""
import random
import pygame
from models.entity import Entity
from models.card import (
    StrikeCard, DefendCard, BashCard, IronWaveCard, FlexCard, CleaveCard,
    NeutralizeCard, DeadlyPoisonCard, BladeDanceCard, ShadowstepCard,
    SoulDrainCard, OfferingCard, CorpseExplosionCard, WarcryCard,
    ZapCard, FrostBarrierCard, ThunderStrikeCard, StaticDischargeCard,
    SmiteCard, HolyShieldCard, ConsecrationCard, RadiantVowCard
)
from models.relic import (
    BurningBloodRelic, RingOfTheSerpentRelic, SoulPhylacteryRelic,
    StormCoreRelic, SunCrestRelic, Relic
)
from models.potion import HealthPotion
from engine.sound import play_sfx
from settings import MAX_HAND_SIZE

class Player(Entity):
    def __init__(self, char_id: str = "blood_knight"):
        self.char_id = char_id
        
        if char_id == "shadow_assassin":
            name = "Shadow Assassin"
            self.class_title = "Nightshade Weaver"
            max_hp = 75
        elif char_id == "void_necromancer":
            name = "Void Necromancer"
            self.class_title = "Scion of the Abyss"
            max_hp = 76
        elif char_id == "tempest_herald":
            name = "Tempest Herald"
            self.class_title = "Conduit of the Storm"
            max_hp = 76
        elif char_id == "radiant_templar":
            name = "Radiant Templar"
            self.class_title = "Champion of the Dawn"
            max_hp = 88
        else:
            name = "Blood Knight"
            self.class_title = "Vanguard of Ruin"
            max_hp = 84

        super().__init__(name, max_hp)
        self.max_energy = 3
        self.energy = self.max_energy
        self.gold = 99

        # Combat Piles
        self.draw_pile = []
        self.hand = []
        self.discard_pile = []
        self.exhaust_pile = []
        self.max_hand_size = MAX_HAND_SIZE

        # Relics and Potions
        self.relics: list[Relic] = []
        self.potions = [HealthPotion(), None, None]

        # Screen position
        self.x = 180
        self.y = 260
        self.width = 130
        self.height = 170

        # Build Starter Deck & Starter Relic based on character class
        self.deck = self._build_starter_deck()
        self._assign_starter_relic()

    def _build_starter_deck(self):
        deck = []
        for _ in range(4):
            deck.append(StrikeCard())
        for _ in range(4):
            deck.append(DefendCard())

        if self.char_id == "shadow_assassin":
            deck.append(NeutralizeCard())
            deck.append(DeadlyPoisonCard())
            deck.append(BladeDanceCard())
            deck.append(ShadowstepCard())
        elif self.char_id == "void_necromancer":
            deck.append(SoulDrainCard())
            deck.append(OfferingCard())
            deck.append(CorpseExplosionCard())
            deck.append(WarcryCard())
        elif self.char_id == "tempest_herald":
            deck.append(ZapCard())
            deck.append(FrostBarrierCard())
            deck.append(ThunderStrikeCard())
            deck.append(StaticDischargeCard())
        elif self.char_id == "radiant_templar":
            deck.append(SmiteCard())
            deck.append(HolyShieldCard())
            deck.append(ConsecrationCard())
            deck.append(RadiantVowCard())
        else: # blood_knight
            deck.append(BashCard())
            deck.append(IronWaveCard())
            deck.append(FlexCard())
            deck.append(CleaveCard())
        return deck

    def _assign_starter_relic(self):
        if self.char_id == "shadow_assassin":
            self.add_relic(RingOfTheSerpentRelic())
        elif self.char_id == "void_necromancer":
            self.add_relic(SoulPhylacteryRelic())
        elif self.char_id == "tempest_herald":
            self.add_relic(StormCoreRelic())
        elif self.char_id == "radiant_templar":
            self.add_relic(SunCrestRelic())
        else:
            self.add_relic(BurningBloodRelic())

    def has_relic(self, id_name: str) -> bool:
        return any(r.id_name == id_name for r in self.relics)

    def add_relic(self, relic: Relic):
        self.relics.append(relic)

    def init_combat(self):
        """Prepare draw pile at start of combat."""
        self.block = 0
        self.statuses.clear()
        self.draw_pile = [card.clone() for card in self.deck]
        random.shuffle(self.draw_pile)
        self.hand.clear()
        self.discard_pile.clear()
        self.exhaust_pile.clear()
        self.energy = self.max_energy

    def start_turn(self):
        super().start_turn()
        self.energy = self.max_energy

        # Radiant Templar Thorns lasts only one turn (persists through enemy turn, clears on player turn)
        if self.char_id == "radiant_templar" and self.statuses.has("Thorns"):
            self.statuses.reduce("Thorns", self.statuses.get("Thorns"))

        # Power effects: Demon Form
        demon_form = self.statuses.get("DemonForm")
        if demon_form > 0:
            self.statuses.apply("Strength", demon_form)

        # Draw hand (default 5 cards)
        self.draw_cards(5)

    def add_card_to_hand(self, card) -> bool:
        """Adds a card directly to hand if under max hand size limit."""
        if len(self.hand) < self.max_hand_size:
            self.hand.append(card)
            return True
        return False

    def draw_cards(self, count: int):
        for _ in range(count):
            if len(self.hand) >= self.max_hand_size:
                break
            if not self.draw_pile:
                if not self.discard_pile:
                    break
                self.draw_pile = self.discard_pile.copy()
                self.discard_pile.clear()
                random.shuffle(self.draw_pile)

            if self.draw_pile:
                card = self.draw_pile.pop()
                self.hand.append(card)
                play_sfx('card_draw', 0.25)

    def discard_hand(self):
        if self.has_relic("runic_pyramid"):
            return
        for card in self.hand:
            self.discard_pile.append(card)
        self.hand.clear()

    def draw(self, surface):
        """Renders custom dark fantasy hero avatar depending on class."""
        from engine.character_renderer import CharacterRenderer
        px = int(self.x + self.lunge_x)
        flash = self.flash_timer > 0
        CharacterRenderer.get().draw_hero(surface, self.char_id, px, self.y, self.width, self.height, flash=flash)

    def _draw_tempest(self, surface, flash):
        # Tempest Herald: Electric sapphire robes, lightning catalyst, storm aura
        glow = (60, 170, 255)
        robe_col = (255, 255, 255) if flash else (25, 45, 80)
        trim_col = (255, 255, 255) if flash else (80, 200, 255)

        aura = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (*glow, 50), (10, 20, self.width + 20, self.height))
        surface.blit(aura, (self.x - 20, self.y - 10))

        # Flowing Robes
        p1 = (self.x + self.width // 2, self.y + 35)
        p2 = (self.x + self.width + 10, self.y + self.height)
        p3 = (self.x - 10, self.y + self.height)
        pygame.draw.polygon(surface, robe_col, [p1, p2, p3])
        pygame.draw.polygon(surface, trim_col, [p1, p2, p3], 2)

        # Chest rune
        chest = pygame.Rect(self.x + 30, self.y + 55, self.width - 60, 55)
        pygame.draw.rect(surface, (18, 32, 60), chest, border_radius=4)
        pygame.draw.line(surface, (100, 220, 255), (self.x + self.width // 2, self.y + 60), (self.x + self.width // 2, self.y + 100), 3)

        # Sorcerer Hood & Electric Eyes
        head = (self.x + self.width // 2, self.y + 32)
        pygame.draw.circle(surface, (20, 35, 65), head, 24)
        pygame.draw.circle(surface, (120, 230, 255), (head[0] - 7, head[1]), 3)
        pygame.draw.circle(surface, (120, 230, 255), (head[0] + 7, head[1]), 3)

        # Levitating Storm Catalyst (Right Hand)
        orb_center = (self.x + self.width + 18, self.y + 60)
        pygame.draw.circle(surface, (80, 190, 255), orb_center, 12)
        pygame.draw.circle(surface, (220, 245, 255), orb_center, 6)
        # Lightning sparks around orb
        pygame.draw.line(surface, (255, 255, 255), (orb_center[0] - 8, orb_center[1] - 8), (orb_center[0] + 8, orb_center[1] + 8), 2)

    def _draw_templar(self, surface, flash):
        # Radiant Templar: Gilded plate armor, sun crest shield, holy warhammer
        glow = (255, 215, 60)
        body_col = (255, 255, 255) if flash else (65, 55, 30)
        armor_col = (255, 255, 255) if flash else (220, 180, 50)

        aura = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (*glow, 45), (10, 20, self.width + 20, self.height))
        surface.blit(aura, (self.x - 20, self.y - 10))

        # Golden Tabard
        p1 = (self.x + self.width // 2, self.y + 35)
        p2 = (self.x + self.width + 12, self.y + self.height)
        p3 = (self.x - 12, self.y + self.height)
        pygame.draw.polygon(surface, body_col, [p1, p2, p3])

        # Gilded Breastplate
        chest = pygame.Rect(self.x + 24, self.y + 48, self.width - 48, 65)
        pygame.draw.rect(surface, armor_col, chest, border_radius=6)
        pygame.draw.rect(surface, (255, 240, 140), chest, width=2, border_radius=6)

        # Sun Cross emblem on chest
        cx = self.x + self.width // 2
        cy = self.y + 80
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 8)
        pygame.draw.line(surface, (255, 255, 255), (cx - 10, cy), (cx + 10, cy), 3)
        pygame.draw.line(surface, (255, 255, 255), (cx, cy - 10), (cx, cy + 10), 3)

        # Templar Great Helm
        head = (self.x + self.width // 2, self.y + 32)
        pygame.draw.circle(surface, (180, 150, 40), head, 26)
        # Golden Cross Visor
        pygame.draw.line(surface, (255, 240, 180), (head[0] - 14, head[1]), (head[0] + 14, head[1]), 3)
        pygame.draw.line(surface, (255, 240, 180), (head[0], head[1] - 12), (head[0], head[1] + 12), 3)

        # Holy Warhammer (Right Hand)
        mace_p1 = (self.x + self.width + 15, self.y + self.height - 10)
        mace_p2 = (self.x + self.width + 25, self.y + 10)
        pygame.draw.line(surface, (150, 130, 90), mace_p1, mace_p2, 5)
        # Radiant hammer head
        pygame.draw.rect(surface, (255, 220, 80), (mace_p2[0] - 12, mace_p2[1] - 10, 24, 18), border_radius=3)


    def _draw_knight(self, surface, flash):
        # Blood Knight: heavy red & obsidian plate, two-handed sword
        glow = (220, 50, 60)
        body_col = (255, 255, 255) if flash else (65, 45, 55)
        armor_col = (255, 255, 255) if flash else (160, 40, 50)

        # Aura
        aura = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (*glow, 45), (10, 20, self.width + 20, self.height))
        surface.blit(aura, (self.x - 20, self.y - 10))

        # Heavy armor cape
        p1 = (self.x + self.width // 2, self.y + 40)
        p2 = (self.x + self.width + 15, self.y + self.height)
        p3 = (self.x - 15, self.y + self.height)
        pygame.draw.polygon(surface, body_col, [p1, p2, p3])

        # Plate chest
        chest = pygame.Rect(self.x + 25, self.y + 50, self.width - 50, 65)
        pygame.draw.rect(surface, armor_col, chest, border_radius=6)
        pygame.draw.rect(surface, (230, 180, 190), chest, width=2, border_radius=6)

        # Spiked Great helm
        head_center = (self.x + self.width // 2, self.y + 35)
        pygame.draw.circle(surface, (45, 30, 38), head_center, 28)
        # Visor slit
        pygame.draw.line(surface, (255, 60, 70), (self.x + self.width // 2 - 12, self.y + 35), (self.x + self.width // 2 + 12, self.y + 35), 3)

        # Broadsword
        blade_p1 = (self.x + self.width, self.y + 45)
        blade_p2 = (self.x + self.width + 30, self.y - 25)
        pygame.draw.line(surface, (220, 220, 230), blade_p1, blade_p2, 6)
        pygame.draw.line(surface, (255, 80, 90), blade_p1, blade_p2, 3)

    def _draw_assassin(self, surface, flash):
        # Shadow Assassin: sleek emerald cloak, twin venom daggers
        glow = (40, 210, 120)
        body_col = (255, 255, 255) if flash else (30, 45, 38)
        cloak_col = (255, 255, 255) if flash else (45, 110, 75)

        aura = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (*glow, 40), (10, 20, self.width + 20, self.height))
        surface.blit(aura, (self.x - 20, self.y - 10))

        # Ninja cloak
        p1 = (self.x + self.width // 2, self.y + 35)
        p2 = (self.x + self.width + 5, self.y + self.height)
        p3 = (self.x - 5, self.y + self.height)
        pygame.draw.polygon(surface, cloak_col, [p1, p2, p3])

        # Dark vest
        chest = pygame.Rect(self.x + 30, self.y + 55, self.width - 60, 60)
        pygame.draw.rect(surface, body_col, chest, border_radius=4)

        # Hood & Glowing eyes
        head_center = (self.x + self.width // 2, self.y + 35)
        pygame.draw.circle(surface, (25, 35, 30), head_center, 24)
        pygame.draw.circle(surface, (80, 255, 140), (head_center[0] - 7, head_center[1]), 3)
        pygame.draw.circle(surface, (80, 255, 140), (head_center[0] + 7, head_center[1]), 3)

        # Dual Daggers
        d1_p1 = (self.x + self.width - 5, self.y + 70)
        d1_p2 = (self.x + self.width + 25, self.y + 20)
        pygame.draw.line(surface, (100, 245, 160), d1_p1, d1_p2, 3)

        d2_p1 = (self.x + 5, self.y + 70)
        d2_p2 = (self.x - 20, self.y + 20)
        pygame.draw.line(surface, (100, 245, 160), d2_p1, d2_p2, 3)

    def _draw_necromancer(self, surface, flash):
        # Void Necromancer: purple occult robes, skeletal horns, mystic soul staff
        glow = (160, 70, 230)
        robe_col = (255, 255, 255) if flash else (50, 30, 68)
        trim_col = (255, 255, 255) if flash else (130, 70, 180)

        aura = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (*glow, 45), (10, 20, self.width + 20, self.height))
        surface.blit(aura, (self.x - 20, self.y - 10))

        # Flowing Sorcerer Robes
        p1 = (self.x + self.width // 2, self.y + 30)
        p2 = (self.x + self.width + 12, self.y + self.height)
        p3 = (self.x - 12, self.y + self.height)
        pygame.draw.polygon(surface, robe_col, [p1, p2, p3])
        pygame.draw.polygon(surface, trim_col, [p1, p2, p3], 2)

        # Horned Skull Mask
        head = (self.x + self.width // 2, self.y + 30)
        pygame.draw.circle(surface, (230, 225, 240), head, 22)
        # Void eye sockets
        pygame.draw.circle(surface, (80, 20, 120), (head[0] - 6, head[1]), 4)
        pygame.draw.circle(surface, (80, 20, 120), (head[0] + 6, head[1]), 4)
        # Horns
        pygame.draw.line(surface, (190, 180, 210), (head[0] - 12, head[1] - 10), (head[0] - 25, head[1] - 30), 3)
        pygame.draw.line(surface, (190, 180, 210), (head[0] + 12, head[1] - 10), (head[0] + 25, head[1] - 30), 3)

        # Soul Staff
        staff_p1 = (self.x + self.width + 15, self.y + self.height - 10)
        staff_p2 = (self.x + self.width + 15, self.y - 20)
        pygame.draw.line(surface, (120, 110, 140), staff_p1, staff_p2, 4)
        # Flaming soul orb atop staff
        pygame.draw.circle(surface, (200, 100, 255), staff_p2, 10)
        pygame.draw.circle(surface, (255, 255, 255), staff_p2, 4)
