"""
Combat system managing turns, card execution, combo counters, damage resolution, and hooks.
"""
from models.player import Player
from models.enemy import Enemy
from models.card import Card, CardType, TargetType
from engine.sound import play_sfx
from engine.particles import ParticleManager
from engine.visual_fx import ScreenShake
from settings import (
    COLOR_HEALTH_RED, COLOR_BLOCK_BLUE, COLOR_TEXT_LIGHT
)

class CombatState:
    def __init__(self, player: Player, enemies: list[Enemy], particle_mgr: ParticleManager, screen_shake: ScreenShake):
        self.player = player
        self.enemies = enemies
        self.particle_mgr = particle_mgr
        self.screen_shake = screen_shake
        
        self.turn = 1
        self.phase = "player_turn"  # 'player_turn', 'enemy_turn', 'victory', 'defeat'
        self.selected_card: Card = None
        self.targeting_active = False

        # Combo and synergy counters
        self.cards_played_this_turn = 0
        self.attacks_played_this_turn = 0
        self.skills_played_this_turn = 0
        self.times_player_damaged = 0
        self.cards_exhausted_this_combat = 0

        # Action banner and enemy pacing stages
        self.combat_banner = ""
        self.banner_timer = 0.0
        self.enemy_stage = "idle"
        self.enemy_stage_timer = 0.0
        self.current_acting_enemy_idx = 0
        self.acting_enemy = None

        # Position enemies dynamically across the right side of the screen
        total_enemies = len(enemies)
        start_x = 720 if total_enemies <= 2 else 650
        spacing = 200 if total_enemies <= 2 else 170

        for i, enemy in enumerate(enemies):
            enemy.x = start_x + i * spacing
            enemy.y = 250
            if enemy.is_boss:
                enemy.y = 210

        # Start combat
        self.start_combat()

    def start_combat(self):
        self.player.init_combat()
        self.times_player_damaged = 0
        self.cards_exhausted_this_combat = 0
        self.anger_plays_this_turn = 0

        # Decide enemy initial intents
        for enemy in self.enemies:
            enemy.decide_intent(self)

        # Start player turn 1
        self.start_player_turn()

        # Trigger relics on combat start (so turn 1 block and buffs are active)
        for relic in self.player.relics:
            relic.on_combat_start(self, self.player)

    def start_player_turn(self):
        self.phase = "player_turn"
        self.cards_played_this_turn = 0
        self.attacks_played_this_turn = 0
        self.skills_played_this_turn = 0
        self.anger_plays_this_turn = 0
        
        self.player.start_turn()

        # Infinite Blades power: add 1 Shiv to hand if space permits
        if self.player.statuses.has("InfiniteBlades"):
            from models.card import ShivCard
            self.player.add_card_to_hand(ShivCard())

        # Trigger relics turn start
        for relic in self.player.relics:
            relic.on_turn_start(self, self.player, self.turn)

        # Trigger Noxious Fumes if player has it
        fumes = self.player.statuses.get("NoxiousFumes")
        if fumes > 0:
            for enemy in self.enemies:
                if enemy.is_alive():
                    enemy.statuses.apply("Poison", fumes)
                    self.spawn_poison_fx(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2)

    def get_card_cost(self, card: Card) -> int:
        """Calculates dynamic card cost accounting for Corruption and discounts."""
        if self.player.statuses.has("Corruption") and card.card_type == CardType.SKILL:
            return 0
        if hasattr(card, "get_dynamic_cost"):
            return card.get_dynamic_cost(self)
        return card.cost

    def can_play_card(self, card: Card) -> bool:
        if self.phase != "player_turn":
            return False
        if card.id_name == "anger" and self.anger_plays_this_turn >= 3:
            return False
        return self.player.energy >= self.get_card_cost(card)

    def play_card(self, card: Card, target: Enemy = None):
        if not self.can_play_card(card):
            return False

        if card.target_type == TargetType.ENEMY and (target is None or not target.is_alive()):
            return False

        effective_cost = self.get_card_cost(card)
        self.player.energy -= effective_cost

        # Remove from hand
        if card in self.player.hand:
            self.player.hand.remove(card)

        # Combo Tracking
        self.cards_played_this_turn += 1
        if card.card_type == CardType.ATTACK:
            self.attacks_played_this_turn += 1
        elif card.card_type == CardType.SKILL:
            self.skills_played_this_turn += 1

        # Relic hooks
        for relic in self.player.relics:
            relic.on_card_played(self, self.player, card)

        # Multi-Cast Checks: DoubleTap for Attacks, Burst for Skills
        cast_times = 1
        if card.card_type == CardType.ATTACK and self.player.statuses.get("DoubleTap") > 0:
            self.player.statuses.reduce("DoubleTap", 1)
            cast_times = 2
            self.spawn_buff_fx(self.player.x + 60, self.player.y + 60)
        elif card.card_type == CardType.SKILL and self.player.statuses.get("Burst") > 0:
            self.player.statuses.reduce("Burst", 1)
            cast_times = 2
            self.spawn_buff_fx(self.player.x + 60, self.player.y + 60)

        # Execute card effect(s)
        for _ in range(cast_times):
            if card.target_type == TargetType.ENEMY and target and not target.is_alive():
                # Re-target another alive enemy if original died in multi-cast
                alive = [e for e in self.enemies if e.is_alive()]
                if alive:
                    target = alive[0]
                else:
                    break
            card.play(self, self.player, target)

        # Corruption synergy: force skills to exhaust
        # Power cards (purple cards) always exhaust when played so they are never redrawn
        is_exhaust = card.exhaust or card.card_type == CardType.POWER or (self.player.statuses.has("Corruption") and card.card_type == CardType.SKILL)

        if is_exhaust:
            self.exhaust_card(card)
        else:
            self.player.discard_pile.append(card)

        # Check enemy deaths and combat resolution
        self.check_combat_status()
        return True

    def exhaust_card(self, card: Card):
        """Exhausts a card and activates Feel No Pain & Dark Embrace synergies."""
        if card in self.player.hand:
            self.player.hand.remove(card)
        if card not in self.player.exhaust_pile:
            self.player.exhaust_pile.append(card)
        self.cards_exhausted_this_combat += 1

        # Feel No Pain hook: gain Block
        fnp = self.player.statuses.get("FeelNoPain")
        if fnp > 0:
            self.player.gain_block(fnp)
            self.spawn_block_fx(self.player.x + 60, self.player.y + 70)

        # Dark Embrace hook: draw a card
        de = self.player.statuses.get("DarkEmbrace")
        if de > 0:
            self.player.draw_cards(de)

    def player_take_card_damage(self, amount: int):
        """Processes self-inflicted damage from card effects and triggers Rupture."""
        self.player.hp = max(1, self.player.hp - amount)
        self.times_player_damaged += 1
        play_sfx('debuff', 0.5)
        self.particle_mgr.spawn_popup(self.player.x + 40, self.player.y + 20, f"-{amount} Self", (220, 40, 40))

        # Rupture hook: gain Strength on self-harm
        rupture = self.player.statuses.get("Rupture")
        if rupture > 0:
            self.player.statuses.apply("Strength", rupture)
            self.spawn_buff_fx(self.player.x + 60, self.player.y + 60)

    def deal_attack_damage(self, attacker, defender, raw_damage: int, heavy: bool = False) -> tuple[int, int]:
        hp_loss, block_loss = defender.take_damage(raw_damage, is_attack=True)

        if defender == self.player and hp_loss > 0:
            self.times_player_damaged += 1

        # Audio and Visuals
        if heavy:
            play_sfx('heavy_hit', 0.8)
            self.screen_shake.start(intensity=9.0, duration=0.3)
        else:
            play_sfx('attack', 0.6)
            self.screen_shake.start(intensity=4.0, duration=0.15)

        cx = defender.x + defender.width // 2
        cy = defender.y + defender.height // 2

        self.particle_mgr.spawn_slash(cx, cy)
        if hp_loss > 0:
            self.particle_mgr.spawn_popup(cx, cy - 30, f"-{hp_loss}", COLOR_HEALTH_RED, is_crit=heavy)
        if block_loss > 0:
            self.particle_mgr.spawn_popup(cx - 25, cy - 10, f"Blocked {block_loss}", COLOR_BLOCK_BLUE)

        # Thorns response
        thorns = defender.statuses.get("Thorns")
        if thorns > 0 and attacker.is_alive():
            att_hp, _ = attacker.take_damage(thorns, is_attack=False)
            self.particle_mgr.spawn_popup(attacker.x + 30, attacker.y, f"-{thorns} Thorns", COLOR_HEALTH_RED)

        # Flame Barrier response: retaliates when attacked
        fb = defender.statuses.get("FlameBarrier")
        if fb > 0 and attacker.is_alive():
            att_hp, _ = attacker.take_damage(fb, is_attack=False)
            self.particle_mgr.spawn_popup(attacker.x + 30, attacker.y + 20, f"-{fb} Flame", (255, 120, 40))

        # Envenom response: whenever player's Attack deals unblocked damage to an enemy, apply Poison
        if attacker == self.player and defender != self.player and hp_loss > 0 and defender.is_alive():
            envenom = attacker.statuses.get("Envenom")
            if envenom > 0:
                defender.statuses.apply("Poison", envenom)
                self.spawn_poison_fx(cx, cy)
                self.particle_mgr.spawn_popup(cx + 25, cy - 20, f"+{envenom} Poison", (100, 240, 80))

        # Check deaths immediately for corpse explosion
        if not defender.is_alive():
            self._handle_entity_death(defender)

        return hp_loss, block_loss

    def _handle_entity_death(self, entity):
        if entity != self.player and entity.statuses.has("CorpseExplosion"):
            # Corpse Explosion detonation!
            explosion_dmg = entity.max_hp
            play_sfx('heavy_hit', 0.9)
            self.screen_shake.start(intensity=9.0, duration=0.35)
            cx = entity.x + entity.width // 2
            cy = entity.y + entity.height // 2
            self.particle_mgr.spawn_burst(cx, cy, (100, 240, 80), count=32, speed=6.5)

            for other in self.enemies:
                if other.is_alive() and other != entity:
                    hp_dmg, _ = other.take_damage(explosion_dmg, is_attack=False)
                    self.particle_mgr.spawn_popup(other.x + other.width // 2, other.y + other.height // 2, f"-{explosion_dmg} BOOM!", (120, 255, 90), is_crit=True)

    def spawn_block_fx(self, x, y):
        play_sfx('block', 0.6)
        self.particle_mgr.spawn_block(x, y)

    def spawn_poison_fx(self, x, y):
        play_sfx('magic', 0.5)
        self.particle_mgr.spawn_poison(x, y)

    def spawn_buff_fx(self, x, y):
        play_sfx('buff', 0.6)
        self.particle_mgr.spawn_burst(x, y, (240, 210, 80), count=18, speed=3.5)

    def spawn_debuff_fx(self, x, y):
        play_sfx('debuff', 0.6)
        self.particle_mgr.spawn_burst(x, y, (190, 80, 240), count=18, speed=3.5)

    def set_banner(self, text: str, duration: float = 1.4):
        self.combat_banner = text
        self.banner_timer = duration

    def end_player_turn(self):
        if self.phase != "player_turn":
            return

        # Combustion trigger: lose 1 HP, deal AoE damage
        combustion = self.player.statuses.get("Combustion")
        if combustion > 0:
            self.player_take_card_damage(1)
            for enemy in self.enemies:
                if enemy.is_alive():
                    enemy.take_damage(combustion, is_attack=False)
                    self.particle_mgr.spawn_popup(enemy.x + enemy.width // 2, enemy.y + 40, f"-{combustion} Burn", (255, 140, 40))

        self.player.end_turn()
        self.player.discard_hand()

        for relic in self.player.relics:
            relic.on_turn_end(self, self.player)

        self.phase = "enemy_turn"
        self.enemy_stage = "poison"
        self.enemy_stage_timer = 0.4
        self.current_acting_enemy_idx = 0
        self.acting_enemy = None
        self.set_banner("⚔️ ENEMY TURN ⚔️", 1.2)

    def update(self, dt):
        self.player.update(dt)
        for enemy in self.enemies:
            enemy.update(dt)

        if self.banner_timer > 0:
            self.banner_timer -= dt
            if self.banner_timer <= 0:
                self.combat_banner = ""

        if self.phase == "enemy_turn":
            self.enemy_stage_timer -= dt
            if self.enemy_stage_timer <= 0:
                if self.enemy_stage == "poison":
                    poison_triggered = False
                    for enemy in self.enemies:
                        if enemy.is_alive() and enemy.statuses.has("Poison"):
                            poison = enemy.statuses.get("Poison")
                            hp_loss, _ = enemy.take_damage(poison, is_attack=False)
                            self.particle_mgr.spawn_popup(enemy.x + enemy.width // 2, enemy.y + 20, f"-{poison} Poison", (100, 240, 100))
                            enemy.statuses.reduce("Poison", 1)
                            self.spawn_poison_fx(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2)
                            if not enemy.is_alive():
                                self._handle_entity_death(enemy)
                            poison_triggered = True

                    self.check_combat_status()
                    if self.phase == "victory":
                        return

                    self.enemy_stage = "actions"
                    self.enemy_stage_timer = 0.6 if poison_triggered else 0.2

                elif self.enemy_stage == "actions":
                    # Advance to next alive enemy
                    while self.current_acting_enemy_idx < len(self.enemies) and not self.enemies[self.current_acting_enemy_idx].is_alive():
                        self.current_acting_enemy_idx += 1

                    if self.current_acting_enemy_idx < len(self.enemies):
                        enemy = self.enemies[self.current_acting_enemy_idx]
                        self.acting_enemy = enemy
                        if self.player.is_alive():
                            enemy.start_turn()
                            enemy.target_lunge_x = -45.0  # Physical attack lunge!
                            desc = enemy.intent.desc if enemy.intent else "Attacks"
                            self.set_banner(f"{enemy.name}: {desc}", 1.4)
                            enemy.execute_turn(self, self.player)
                            enemy.end_turn()

                            if not self.player.is_alive():
                                self.phase = "defeat"
                                play_sfx('debuff', 0.8)
                                return

                        self.current_acting_enemy_idx += 1
                        # Deliberate pause: 0.85 seconds to clearly see attack, popup, and result!
                        self.enemy_stage_timer = 0.85
                    else:
                        self.acting_enemy = None
                        self.enemy_stage = "finish"
                        self.enemy_stage_timer = 0.4

                elif self.enemy_stage == "finish":
                    self.check_combat_status()
                    if self.phase in ("victory", "defeat"):
                        return

                    self.turn += 1
                    for enemy in self.enemies:
                        if enemy.is_alive():
                            enemy.decide_intent(self)

                    self.start_player_turn()
                    self.set_banner(f"TURN {self.turn} - YOUR TURN", 1.5)

    def resolve_all_enemy_turns(self):
        """Immediately resolves all staged enemy actions until player turn resumes."""
        max_steps = 50
        while self.phase == "enemy_turn" and max_steps > 0:
            self.enemy_stage_timer = 0.0
            self.update(0.1)
            max_steps -= 1

    def check_combat_status(self):
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if not alive_enemies:
            self.phase = "victory"
            play_sfx('victory', 0.7)
            for relic in self.player.relics:
                relic.on_combat_end(self, self.player, won=True)
        elif not self.player.is_alive():
            self.phase = "defeat"
            for relic in self.player.relics:
                relic.on_combat_end(self, self.player, won=False)
