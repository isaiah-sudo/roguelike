"""
Enemy AI, Intent System, Enemy Types, and Fighting Styles Catalog:
- Undead: Crypt Cultist (Scaler), Skeleton Sentinel (Turtle), Tormented Wight (Drainer)
- Beast / Vermin: Plague Fiend (Poisoner), Dread Spider (Web Spinner & Multi-Bite)
- Demon / Abyssal: Void Reaver (Berserker / Rage), Cinder Demon (Pyromancer / Thorns)
- Arcane / Occult: Mad Alchemist (Brewer / Buffs), Corrupted Hierophant (Curser)
- Bosses: Necrolord Malakor (Lich King), Void Behemoth (Abyssal Titan)
"""
from enum import Enum
import random
import pygame
from models.entity import Entity
from settings import (
    COLOR_INTENT_ATTACK, COLOR_INTENT_DEFEND, COLOR_INTENT_BUFF, COLOR_INTENT_DEBUFF,
    FONTS
)

class EnemyType(Enum):
    UNDEAD = "Undead"
    BEAST = "Beast"
    DEMON = "Demon"
    ARCANE = "Arcane"
    BOSS = "Boss"

class IntentType(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    BUFF = "buff"
    DEBUFF = "debuff"
    ATTACK_DEBUFF = "attack_debuff"

class Intent:
    def __init__(self, intent_type: IntentType, damage: int = 0, hits: int = 1, desc: str = ""):
        self.intent_type = intent_type
        self.damage = damage
        self.hits = hits
        self.desc = desc

    def get_display_text(self, enemy) -> str:
        if self.intent_type in (IntentType.ATTACK, IntentType.ATTACK_DEBUFF):
            str_val = enemy.statuses.get("Strength")
            weak = enemy.statuses.has("Weak")
            dmg = max(0, self.damage + str_val)
            if weak:
                dmg = int(dmg * 0.75)
            if self.hits > 1:
                return f"{dmg}x{self.hits}"
            return f"{dmg}"
        elif self.intent_type == IntentType.DEFEND:
            return "Defend"
        elif self.intent_type == IntentType.BUFF:
            return "Buff"
        elif self.intent_type == IntentType.DEBUFF:
            return "Curse"
        return ""

class Enemy(Entity):
    def __init__(self, name: str, max_hp: int, enemy_type: EnemyType = EnemyType.UNDEAD, is_elite: bool = False, is_boss: bool = False):
        super().__init__(name, max_hp)
        self.enemy_type = enemy_type
        self.is_elite = is_elite
        self.is_boss = is_boss
        self.intent = None
        self.turn_count = 0
        self.color_primary = (160, 50, 70)
        self.color_secondary = (60, 30, 40)
        self.width = 130
        self.height = 160

    def decide_intent(self, combat_state):
        raise NotImplementedError

    def execute_turn(self, combat_state, player):
        raise NotImplementedError

    def draw_intent(self, surface):
        if not self.intent or not self.is_alive():
            return
        ex = int(self.x + self.lunge_x)
        ix = ex + self.width // 2
        iy = self.y - 35

        itype = self.intent.intent_type
        if itype in (IntentType.ATTACK, IntentType.ATTACK_DEBUFF):
            color = COLOR_INTENT_ATTACK
            pygame.draw.line(surface, color, (ix - 12, iy - 6), (ix + 12, iy + 6), 3)
            pygame.draw.line(surface, (255, 255, 255), (ix - 8, iy - 4), (ix + 8, iy + 4), 1)
        elif itype == IntentType.DEFEND:
            color = COLOR_INTENT_DEFEND
            pygame.draw.polygon(surface, color, [
                (ix, iy - 10), (ix + 10, iy - 5), (ix, iy + 10), (ix - 10, iy - 5)
            ])
        else:
            color = COLOR_INTENT_BUFF if itype == IntentType.BUFF else COLOR_INTENT_DEBUFF
            pygame.draw.circle(surface, color, (ix, iy), 9)

        text = self.intent.get_display_text(self)
        if text:
            rendered = FONTS['intent'].render(text, True, color)
            rect = rendered.get_rect(center=(ix, iy + 18))
            surface.blit(rendered, rect)

    def draw(self, surface):
        flash = self.flash_timer > 0
        color = (255, 255, 255) if flash else self.color_primary
        bg = (240, 200, 200) if flash else self.color_secondary
        ex = int(self.x + self.lunge_x)

        # Monster body
        rect = pygame.Rect(ex + 15, self.y + 30, self.width - 30, self.height - 40)
        pygame.draw.rect(surface, bg, rect, border_radius=12)
        pygame.draw.rect(surface, color, rect, width=3, border_radius=12)

        # Spikes / Horns
        horn_pts_left = [(ex + 20, self.y + 30), (ex + 5, self.y + 5), (ex + 35, self.y + 25)]
        horn_pts_right = [(ex + self.width - 20, self.y + 30), (ex + self.width - 5, self.y + 5), (ex + self.width - 35, self.y + 25)]
        pygame.draw.polygon(surface, color, horn_pts_left)
        pygame.draw.polygon(surface, color, horn_pts_right)

        # Eyes
        eye_y = self.y + 60
        eye_color = (255, 240, 80) if not self.is_boss else (255, 40, 50)
        pygame.draw.circle(surface, eye_color, (ex + 40, eye_y), 6)
        pygame.draw.circle(surface, eye_color, (ex + self.width - 40, eye_y), 6)

        # Boss crown
        if self.is_boss:
            crown_pts = [
                (ex + 30, self.y + 20),
                (ex + 45, self.y - 10),
                (ex + self.width // 2, self.y + 5),
                (ex + self.width - 45, self.y - 10),
                (ex + self.width - 30, self.y + 20)
            ]
            pygame.draw.polygon(surface, (255, 215, 0), crown_pts)

        self.draw_intent(surface)

# ==========================================
# 1. UNDEAD ENEMIES
# ==========================================

class CryptCultist(Enemy):
    def __init__(self):
        super().__init__("Cultist", 50, EnemyType.UNDEAD)
        self.color_primary = (180, 70, 70)
        self.color_secondary = (50, 20, 25)

    def decide_intent(self, combat_state):
        if self.turn_count == 0:
            self.intent = Intent(IntentType.BUFF, desc="Incantation (+3 Ritual)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=6, desc="Dark Strike (6 DMG)")

    def execute_turn(self, combat_state, player):
        if self.turn_count == 0:
            self.statuses.apply("Ritual", 3)
            combat_state.spawn_buff_fx(self.x + 60, self.y + 60)
        else:
            dmg = max(0, 6 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
        self.turn_count += 1

class SkeletonSentinel(Enemy):
    def __init__(self):
        super().__init__("Skeletal Sentinel", 46, EnemyType.UNDEAD)
        self.color_primary = (190, 190, 210)
        self.color_secondary = (45, 45, 55)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.DEFEND, desc="Bone Shield (12 Block)")
        elif cycle == 1:
            self.intent = Intent(IntentType.ATTACK, damage=8, desc="Cleave (8 DMG)")
        else:
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=5, desc="Shatter Strike (Vulnerable)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.gain_block(12)
            combat_state.spawn_block_fx(self.x + 60, self.y + 60)
        elif cycle == 1:
            dmg = max(0, 8 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
        else:
            dmg = max(0, 5 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
            player.statuses.apply("Vulnerable", 2)
        self.turn_count += 1

class TormentedWight(Enemy):
    def __init__(self):
        super().__init__("Tormented Wight", 80, EnemyType.UNDEAD, is_elite=True)
        self.color_primary = (160, 90, 220)
        self.color_secondary = (45, 25, 65)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.DEBUFF, desc="Banshee Scream (Vulnerable + Weak)")
        elif cycle == 1:
            self.intent = Intent(IntentType.ATTACK, damage=14, desc="Soul Harvest")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=7, hits=2, desc="Claw Frenzy")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            player.statuses.apply("Vulnerable", 2)
            player.statuses.apply("Weak", 2)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        elif cycle == 1:
            dmg = max(0, 14 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            hp_loss, _ = combat_state.deal_attack_damage(self, player, dmg, heavy=True)
            if hp_loss > 0:
                self.heal(hp_loss)
        else:
            for _ in range(2):
                dmg = max(0, 7 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        self.turn_count += 1

# ==========================================
# 2. BEAST / VERMIN ENEMIES
# ==========================================

class BloodBat(Enemy):
    def __init__(self):
        super().__init__("Blood Bat", 36, EnemyType.BEAST)
        self.color_primary = (180, 40, 60)
        self.color_secondary = (45, 20, 30)

    def decide_intent(self, combat_state):
        if self.turn_count % 2 == 0:
            self.intent = Intent(IntentType.ATTACK, damage=6, desc="Vampiric Bite (Heals 3)")
        else:
            self.intent = Intent(IntentType.DEBUFF, desc="Ultrasonic Screech (Weak 2)")

    def execute_turn(self, combat_state, player):
        if self.turn_count % 2 == 0:
            dmg = max(0, 6 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            hp_loss, _ = combat_state.deal_attack_damage(self, player, dmg)
            if hp_loss > 0:
                self.heal(3)
        else:
            player.statuses.apply("Weak", 2)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        self.turn_count += 1

class PlagueRat(Enemy):
    def __init__(self):
        super().__init__("Plague Fiend", 40, EnemyType.BEAST)
        self.color_primary = (90, 180, 80)
        self.color_secondary = (30, 50, 30)

    def decide_intent(self, combat_state):
        if self.turn_count % 2 == 0:
            self.intent = Intent(IntentType.ATTACK, damage=4, hits=2, desc="Venomous Bite (4x2)")
        else:
            self.intent = Intent(IntentType.DEBUFF, desc="Toxic Miasma (3 Poison, Weak)")

    def execute_turn(self, combat_state, player):
        if self.turn_count % 2 == 0:
            for _ in range(2):
                dmg = max(0, 4 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        else:
            player.statuses.apply("Poison", 3)
            player.statuses.apply("Weak", 1)
            combat_state.spawn_poison_fx(player.x + 60, player.y + 60)
        self.turn_count += 1

class DreadSpider(Enemy):
    def __init__(self):
        super().__init__("Dread Spider", 44, EnemyType.BEAST)
        self.color_primary = (40, 160, 140)
        self.color_secondary = (20, 45, 40)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.DEBUFF, desc="Web Spit (Weak 2 + Vulnerable 1)")
        elif cycle == 1:
            self.intent = Intent(IntentType.ATTACK, damage=3, hits=3, desc="Furious Pounce (3x3)")
        else:
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=7, desc="Poison Fang (4 Poison)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            player.statuses.apply("Weak", 2)
            player.statuses.apply("Vulnerable", 1)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        elif cycle == 1:
            for _ in range(3):
                dmg = max(0, 3 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        else:
            dmg = max(0, 7 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
            player.statuses.apply("Poison", 4)
            combat_state.spawn_poison_fx(player.x + 60, player.y + 60)
        self.turn_count += 1

# ==========================================
# 3. DEMON / ABYSSAL ENEMIES
# ==========================================

class VoidReaver(Enemy):
    def __init__(self):
        super().__init__("Void Reaver", 88, EnemyType.DEMON, is_elite=True)
        self.color_primary = (180, 40, 90)
        self.color_secondary = (50, 15, 30)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 2
        if cycle == 0:
            self.intent = Intent(IntentType.BUFF, desc="Eldritch Rage (+2 Str, +6 Block)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=14, desc="Rending Cleave (14 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 2
        if cycle == 0:
            self.statuses.apply("Strength", 2)
            self.gain_block(6)
            combat_state.spawn_buff_fx(self.x + 60, self.y + 60)
        else:
            dmg = max(0, 14 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

class CinderDemon(Enemy):
    def __init__(self):
        super().__init__("Cinder Demon", 52, EnemyType.DEMON)
        self.color_primary = (240, 90, 30)
        self.color_secondary = (60, 20, 15)
        # Inherent spikes
        self.statuses.apply("Thorns", 3)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.ATTACK, damage=10, desc="Flame Burst")
        elif cycle == 1:
            self.intent = Intent(IntentType.BUFF, desc="Ignite Core (+2 Str, +2 Thorns)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=4, hits=3, desc="Hellfire Flurry (4x3)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            dmg = max(0, 10 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
        elif cycle == 1:
            self.statuses.apply("Strength", 2)
            self.statuses.apply("Thorns", 2)
            combat_state.spawn_buff_fx(self.x + 60, self.y + 60)
        else:
            for _ in range(3):
                dmg = max(0, 4 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        self.turn_count += 1

# ==========================================
# 4. ARCANE / OCCULT ENEMIES
# ==========================================

class MadAlchemist(Enemy):
    def __init__(self):
        super().__init__("Mad Alchemist", 48, EnemyType.ARCANE)
        self.color_primary = (160, 190, 40)
        self.color_secondary = (40, 50, 20)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.BUFF, desc="Drink Stoneskin Tonic (12 Block, 3 Metal)")
        elif cycle == 1:
            self.intent = Intent(IntentType.DEBUFF, desc="Corrosive Acid (4 Poison, 2 Vuln)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=12, desc="Explosive Flask (12 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.gain_block(12)
            self.statuses.apply("Metallicize", 3)
            combat_state.spawn_buff_fx(self.x + 60, self.y + 60)
        elif cycle == 1:
            player.statuses.apply("Poison", 4)
            player.statuses.apply("Vulnerable", 2)
            combat_state.spawn_poison_fx(player.x + 60, player.y + 60)
        else:
            dmg = max(0, 12 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

class CorruptedHierophant(Enemy):
    def __init__(self):
        super().__init__("Corrupted Hierophant", 58, EnemyType.ARCANE)
        self.color_primary = (210, 160, 70)
        self.color_secondary = (50, 40, 25)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.BUFF, desc="Unholy Benediction (14 Block, Heal 6)")
        elif cycle == 1:
            self.intent = Intent(IntentType.ATTACK, damage=9, desc="Dark Smite (9 DMG)")
        else:
            self.intent = Intent(IntentType.DEBUFF, desc="Penance Word (Weak 2, Vuln 2)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.gain_block(14)
            self.heal(6)
            combat_state.spawn_buff_fx(self.x + 60, self.y + 60)
        elif cycle == 1:
            dmg = max(0, 9 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
        else:
            player.statuses.apply("Weak", 2)
            player.statuses.apply("Vulnerable", 2)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        self.turn_count += 1

# ==========================================
# 5. BOSSES
# ==========================================

class NecrolordMalakor(Enemy):
    def __init__(self):
        super().__init__("Necrolord Malakor", 160, EnemyType.BOSS, is_boss=True)
        self.color_primary = (220, 40, 70)
        self.color_secondary = (50, 15, 30)
        self.width = 170
        self.height = 200

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 4
        if cycle == 0:
            self.intent = Intent(IntentType.BUFF, desc="Soul Barrier (+10 Block, +1 Str)")
        elif cycle == 1:
            self.intent = Intent(IntentType.ATTACK, damage=6, hits=3, desc="Death Ray (6x3)")
        elif cycle == 2:
            self.intent = Intent(IntentType.BUFF, desc="Cataclysm Ritual (Charging!)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=22, desc="Apocalypse Blast (22 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 4
        if cycle == 0:
            self.gain_block(10)
            self.statuses.apply("Strength", 1)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        elif cycle == 1:
            for _ in range(3):
                dmg = max(0, 6 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        elif cycle == 2:
            self.statuses.apply("Strength", 2)
            self.gain_block(8)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        else:
            dmg = max(0, 22 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

class VoidBehemoth(Enemy):
    def __init__(self):
        super().__init__("Void Behemoth", 145, EnemyType.BOSS, is_boss=True)
        self.color_primary = (140, 60, 220)
        self.color_secondary = (35, 20, 55)
        self.width = 170
        self.height = 200

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.ATTACK, damage=4, hits=4, desc="Tentacle Thrash (4x4)")
        elif cycle == 1:
            self.intent = Intent(IntentType.DEBUFF, desc="Abyssal Gaze (Weak 1, Vuln 1, 3 Poison)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=18, desc="Cosmic Devour (18 DMG, Heals 5)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            for _ in range(4):
                dmg = max(0, 4 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        elif cycle == 1:
            player.statuses.apply("Weak", 1)
            player.statuses.apply("Vulnerable", 1)
            player.statuses.apply("Poison", 3)
            combat_state.spawn_poison_fx(player.x + 60, player.y + 60)
        else:
            dmg = max(0, 18 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
            self.heal(5)
        self.turn_count += 1

# ==========================================
# ACT 2: THE MOLTEN BASTION ENEMIES
# ==========================================

class InfernalHound(Enemy):
    def __init__(self):
        super().__init__("Infernal Hound", 48, EnemyType.BEAST)
        self.color_primary = (240, 90, 40)
        self.color_secondary = (70, 25, 20)
        self.width = 130
        self.height = 150

    def decide_intent(self, combat_state):
        if self.turn_count % 2 == 0:
            self.intent = Intent(IntentType.ATTACK, damage=4, hits=3, desc="Triple Bite (4x3)")
        else:
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=7, desc="Cinder Breath (7 DMG + Vuln)")

    def execute_turn(self, combat_state, player):
        if self.turn_count % 2 == 0:
            for _ in range(3):
                dmg = max(0, 4 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        else:
            dmg = max(0, 7 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
            player.statuses.apply("Vulnerable", 2)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        self.turn_count += 1

class ObsidianGolem(Enemy):
    def __init__(self):
        super().__init__("Obsidian Golem", 78, EnemyType.ARCANE)
        self.color_primary = (70, 65, 80)
        self.color_secondary = (30, 25, 38)
        self.width = 140
        self.height = 170

    def decide_intent(self, combat_state):
        if self.turn_count % 3 == 0:
            self.intent = Intent(IntentType.DEFEND, desc="Obsidian Carapace (+22 Block)")
        elif self.turn_count % 3 == 1:
            self.intent = Intent(IntentType.BUFF, desc="Crush Preparation (+3 Str)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=20, desc="Earth Shatter (20 DMG)")

    def execute_turn(self, combat_state, player):
        if self.turn_count % 3 == 0:
            self.gain_block(22)
            combat_state.spawn_block_fx(self.x + self.width // 2, self.y + 70)
        elif self.turn_count % 3 == 1:
            self.statuses.apply("Strength", 3)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        else:
            dmg = max(0, 20 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

class DarkWarlock(Enemy):
    def __init__(self):
        super().__init__("Dark Warlock", 54, EnemyType.DEMON)
        self.color_primary = (160, 40, 180)
        self.color_secondary = (45, 20, 55)

    def decide_intent(self, combat_state):
        if self.turn_count % 2 == 0:
            self.intent = Intent(IntentType.DEBUFF, desc="Hex of Frailty (Weak 2, Vuln 2)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=14, desc="Shadow Bolt (14 DMG)")

    def execute_turn(self, combat_state, player):
        if self.turn_count % 2 == 0:
            player.statuses.apply("Weak", 2)
            player.statuses.apply("Vulnerable", 2)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        else:
            dmg = max(0, 14 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg)
        self.turn_count += 1

class FlameArchon(Enemy):
    def __init__(self):
        super().__init__("Flame Archon", 95, EnemyType.DEMON, is_elite=True)
        self.color_primary = (255, 120, 30)
        self.color_secondary = (60, 25, 20)
        self.statuses.apply("Thorns", 4)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.ATTACK, damage=8, hits=2, desc="Dual Scythes (8x2)")
        elif cycle == 1:
            self.intent = Intent(IntentType.BUFF, desc="Blazing Stance (+2 Str, +14 Block)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=22, desc="Infernal Flare (22 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            for _ in range(2):
                dmg = max(0, 8 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        elif cycle == 1:
            self.statuses.apply("Strength", 2)
            self.gain_block(14)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        else:
            dmg = max(0, 22 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

class CenturionAutomaton(Enemy):
    def __init__(self):
        super().__init__("Centurion Automaton", 115, EnemyType.ARCANE, is_elite=True)
        self.color_primary = (200, 160, 60)
        self.color_secondary = (45, 38, 25)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.DEFEND, desc="Steam Aegis (+25 Block)")
        elif cycle == 1:
            self.intent = Intent(IntentType.BUFF, desc="Charging Hyper Beam (+4 Str)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=28, desc="Hyper Beam (28 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.gain_block(25)
            combat_state.spawn_block_fx(self.x + self.width // 2, self.y + 70)
        elif cycle == 1:
            self.statuses.apply("Strength", 4)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        else:
            dmg = max(0, 28 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

class IgnisTheInfernal(Enemy):
    def __init__(self):
        super().__init__("Ignis the Infernal", 210, EnemyType.BOSS, is_boss=True)
        self.color_primary = (255, 90, 30)
        self.color_secondary = (50, 15, 10)
        self.width = 175
        self.height = 205
        self.statuses.apply("Thorns", 2)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 4
        if cycle == 0:
            self.intent = Intent(IntentType.BUFF, desc="Molten Armor (+18 Block, +1 Str)")
        elif cycle == 1:
            self.intent = Intent(IntentType.ATTACK, damage=6, hits=3, desc="Magma Wave (6x3)")
        elif cycle == 2:
            self.intent = Intent(IntentType.DEBUFF, desc="Suffocating Ash (Weak 1, Vuln 1)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=24, desc="Cataclysm Nova (24 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 4
        if cycle == 0:
            self.gain_block(18)
            self.statuses.apply("Strength", 1)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        elif cycle == 1:
            for _ in range(3):
                dmg = max(0, 6 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        elif cycle == 2:
            player.statuses.apply("Weak", 1)
            player.statuses.apply("Vulnerable", 1)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        else:
            dmg = max(0, 24 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

class ArchmageValerius(Enemy):
    def __init__(self):
        super().__init__("Archmage Valerius", 195, EnemyType.BOSS, is_boss=True)
        self.color_primary = (130, 80, 240)
        self.color_secondary = (30, 20, 50)
        self.width = 170
        self.height = 200

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.ATTACK, damage=4, hits=4, desc="Arcane Missiles (4x4)")
        elif cycle == 1:
            self.intent = Intent(IntentType.DEFEND, desc="Chrono Barrier (+18 Block, +1 Str)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=22, desc="Time Rupture (22 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            for _ in range(4):
                dmg = max(0, 4 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        elif cycle == 1:
            self.gain_block(18)
            self.statuses.apply("Strength", 1)
            combat_state.spawn_block_fx(self.x + self.width // 2, self.y + 70)
        else:
            dmg = max(0, 22 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1

# ==========================================
# ACT 3: THE ABYSSAL CITADEL PINNACLE FOES
# ==========================================

class VoidRevenant(Enemy):
    def __init__(self):
        super().__init__("Void Revenant", 82, EnemyType.UNDEAD)
        self.color_primary = (100, 180, 230)
        self.color_secondary = (20, 35, 50)

    def decide_intent(self, combat_state):
        if self.turn_count % 2 == 0:
            self.intent = Intent(IntentType.BUFF, desc="Phase Shift (Gain Intangible)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=16, desc="Essence Siphon (16 DMG, Heals 8)")

    def execute_turn(self, combat_state, player):
        if self.turn_count % 2 == 0:
            self.statuses.apply("Intangible", 1)
            self.gain_block(15)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        else:
            dmg = max(0, 16 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            hp_loss, _ = combat_state.deal_attack_damage(self, player, dmg)
            if hp_loss > 0:
                self.heal(8)
        self.turn_count += 1

class NemesisAvatar(Enemy):
    def __init__(self):
        super().__init__("Nemesis Avatar", 140, EnemyType.DEMON, is_elite=True)
        self.color_primary = (220, 40, 90)
        self.color_secondary = (45, 15, 25)

    def decide_intent(self, combat_state):
        if self.turn_count % 2 == 0:
            self.intent = Intent(IntentType.BUFF, desc="Death Mantle (+1 Intangible, +1 Str)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=8, hits=3, desc="Reaping Scythe (8x3)")

    def execute_turn(self, combat_state, player):
        if self.turn_count % 2 == 0:
            self.statuses.apply("Intangible", 1)
            self.statuses.apply("Strength", 1)
            combat_state.spawn_buff_fx(self.x + self.width // 2, self.y + 70)
        else:
            for _ in range(3):
                dmg = max(0, 8 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        self.turn_count += 1

class TheCorruptedHeart(Enemy):
    def __init__(self):
        super().__init__("The Corrupted Heart", 320, EnemyType.BOSS, is_boss=True)
        self.color_primary = (255, 30, 50)
        self.color_secondary = (40, 10, 18)
        self.width = 185
        self.height = 215
        self.statuses.apply("Thorns", 1)

    def decide_intent(self, combat_state):
        cycle = self.turn_count % 3
        if cycle == 0:
            self.intent = Intent(IntentType.ATTACK, damage=3, hits=12, desc="Blood Barrage (3x12)")
        elif cycle == 1:
            self.intent = Intent(IntentType.DEBUFF, desc="Echo of Damnation (Weak 1, Vuln 1, +1 Str)")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=28, desc="Heartthrob Cleave (28 DMG)")

    def execute_turn(self, combat_state, player):
        cycle = self.turn_count % 3
        if cycle == 0:
            for _ in range(12):
                dmg = max(0, 3 + self.statuses.get("Strength"))
                if self.statuses.has("Weak"):
                    dmg = int(dmg * 0.75)
                combat_state.deal_attack_damage(self, player, dmg)
        elif cycle == 1:
            player.statuses.apply("Weak", 1)
            player.statuses.apply("Vulnerable", 1)
            self.statuses.apply("Strength", 1)
            combat_state.spawn_debuff_fx(player.x + 60, player.y + 60)
        else:
            dmg = max(0, 28 + self.statuses.get("Strength"))
            if self.statuses.has("Weak"):
                dmg = int(dmg * 0.75)
            combat_state.deal_attack_damage(self, player, dmg, heavy=True)
        self.turn_count += 1
