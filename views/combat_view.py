"""
Combat View: Overhauled with Slay the Spire aesthetics, staged turn feedback,
animated dungeon torches, ambient atmospheric particles, smooth card hover elevation,
animated targeting reticle, and delayed ghost damage health bars.
"""
import pygame
import math
import random
from systems.combat import CombatState
from models.card import TargetType
from engine.card_renderer import draw_card, CARD_WIDTH, CARD_HEIGHT
from engine.visual_fx import draw_targeting_arrow
from engine.ui import Button, draw_top_bar
from engine.character_renderer import CharacterRenderer
from engine.sprite_manager import SpriteManager
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_ENERGY_ORB, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD,
    COLOR_HEALTH_RED, COLOR_HEALTH_BG, COLOR_BLOCK_BLUE, FONTS
)

class CombatView:
    def __init__(self, combat_state: CombatState):
        self.state = combat_state
        self.end_turn_btn = Button((1070, 580, 175, 52), "END TURN", FONTS['medium'], bg_color=(140, 38, 50), hover_color=(180, 48, 62))
        self.hovered_card_idx = -1
        self.targeted_enemy = None
        self.drag_start_pos = None

        # Ambient Torch Sparks & Floating Dungeon Motes
        self.torch_particles = []
        self.ambient_motes = []
        self.anim_time = 0.0

        # Smooth Card Elevation
        self.card_elevations = []

        # Ghost Damage Tracking (entity -> float)
        self.ghost_hp = {}

    def handle_event(self, event, mouse_pos) -> str:
        if self.state.phase == "victory":
            return "victory"
        elif self.state.phase == "defeat":
            return "defeat"

        # End turn button (only responsive during player turn)
        if self.state.phase == "player_turn":
            if self.end_turn_btn.handle_event(event):
                self.state.end_player_turn()
                return "none"

        # Check potion use
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            px = 850
            for i, potion in enumerate(self.state.player.potions):
                p_rect = pygame.Rect(px + i * 42, 8, 34, 34)
                if p_rect.collidepoint(event.pos) and potion is not None:
                    target = None
                    if potion.target_required:
                        alive = [e for e in self.state.enemies if e.is_alive()]
                        if alive:
                            target = alive[0]
                    potion.use(self.state, self.state.player, target)
                    self.state.player.potions[i] = None
                    self.state.check_combat_status()
                    return "none"

        # Card interactions (only during player turn)
        if self.state.phase == "player_turn":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    card_rects = self._get_hand_card_rects()
                    for idx, (rect, card) in reversed(list(enumerate(card_rects))):
                        if rect.collidepoint(event.pos):
                            if self.state.can_play_card(card):
                                if card.target_type == TargetType.ENEMY:
                                    self.state.selected_card = card
                                    self.state.targeting_active = True
                                    self.drag_start_pos = rect.midtop
                                else:
                                    self.state.play_card(card)
                                    self.hovered_card_idx = -1
                            elif card.id_name == "anger" and self.state.anger_plays_this_turn >= 3:
                                self.state.particle_mgr.spawn_popup(self.state.player.x + 50, self.state.player.y - 10, "Anger Limit (3/turn)!", (255, 120, 100))
                                play_sfx('debuff', 0.5)
                            break
                elif event.button == 3:  # Right click cancels
                    self.state.selected_card = None
                    self.state.targeting_active = False

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.state.targeting_active and self.state.selected_card:
                    target = self._get_enemy_under_pos(event.pos)
                    if target and target.is_alive():
                        self.state.play_card(self.state.selected_card, target)
                    self.state.selected_card = None
                    self.state.targeting_active = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_e):
                    self.state.end_player_turn()
                elif event.key == pygame.K_ESCAPE:
                    self.state.selected_card = None
                    self.state.targeting_active = False

        return "none"

    def _get_enemy_under_pos(self, pos):
        for enemy in self.state.enemies:
            if enemy.is_alive():
                ex = int(enemy.x + enemy.lunge_x)
                rect = pygame.Rect(ex, enemy.y, enemy.width, enemy.height)
                if rect.collidepoint(pos):
                    return enemy
        return None

    def _get_hand_card_rects(self):
        hand = self.state.player.hand
        num_cards = len(hand)
        if num_cards == 0:
            return []

        # Ensure card elevations list matches hand size
        while len(self.card_elevations) < num_cards:
            self.card_elevations.append(0.0)
        while len(self.card_elevations) > num_cards:
            self.card_elevations.pop()

        base_y = 505
        total_width = 780
        spacing = min(CARD_WIDTH + 14, total_width / max(1, num_cards))
        center_x = 580
        start_x = center_x - (spacing * (num_cards - 1) + CARD_WIDTH) / 2

        results = []
        for i, card in enumerate(hand):
            x = start_x + i * spacing
            elev = self.card_elevations[i] if i < len(self.card_elevations) else 0.0
            y = int(base_y + elev)
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            results.append((rect, card))
        return results

    def update(self, dt, mouse_pos):
        self.anim_time += dt
        CharacterRenderer.get().update(dt)
        SpriteManager.get().update(dt)

        # Update staged combat state & timers
        self.state.update(dt)

        # Update ghost health bars
        all_entities = [self.state.player] + self.state.enemies
        for entity in all_entities:
            cur_hp = float(entity.hp)
            if entity not in self.ghost_hp or cur_hp > self.ghost_hp[entity]:
                self.ghost_hp[entity] = cur_hp
            elif cur_hp < self.ghost_hp[entity]:
                # Smooth slide down
                decay = max(24.0 * dt, (self.ghost_hp[entity] - cur_hp) * min(1.0, dt * 6.0))
                self.ghost_hp[entity] = max(cur_hp, self.ghost_hp[entity] - decay)

        # Update button state depending on whose turn it is
        if self.state.phase == "enemy_turn":
            self.end_turn_btn.text = "ENEMY TURN..."
            self.end_turn_btn.enabled = False
            self.end_turn_btn.bg_color = (45, 36, 52)
        else:
            self.end_turn_btn.text = "END TURN"
            self.end_turn_btn.enabled = True
            self.end_turn_btn.bg_color = (140, 38, 50)

        self.end_turn_btn.update(mouse_pos)
        self.state.particle_mgr.update(dt)
        self.state.screen_shake.update(dt)

        # Ambient Torch Sparks
        if random.random() < 0.40:
            self.torch_particles.append([80 + random.uniform(-6, 6), 235, random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.6), random.uniform(0.3, 0.6)])
            self.torch_particles.append([1200 + random.uniform(-6, 6), 235, random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.6), random.uniform(0.3, 0.6)])

        for p in self.torch_particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= dt
        self.torch_particles = [p for p in self.torch_particles if p[4] > 0]

        # Ambient floating dungeon motes
        if random.random() < 0.20 and len(self.ambient_motes) < 35:
            self.ambient_motes.append([
                random.uniform(50, 1230),
                random.uniform(150, 650),
                random.uniform(-0.3, 0.3),
                random.uniform(-0.4, -0.1),
                random.uniform(2.5, 5.0),
                random.uniform(1.2, 2.5)
            ])

        for m in self.ambient_motes:
            m[0] += m[2] + math.sin(self.anim_time * 2.0 + m[1]) * 0.2
            m[1] += m[3]
            m[4] -= dt
        self.ambient_motes = [m for m in self.ambient_motes if m[4] > 0]

        # Hovered card detection
        card_rects = self._get_hand_card_rects()
        self.hovered_card_idx = -1
        if not self.state.targeting_active and self.state.phase == "player_turn":
            for idx, (rect, _) in reversed(list(enumerate(card_rects))):
                if rect.collidepoint(mouse_pos):
                    self.hovered_card_idx = idx
                    break

        # Smooth elevation animation for cards in hand
        for i in range(len(self.card_elevations)):
            target_elev = -34.0 if i == self.hovered_card_idx else 0.0
            self.card_elevations[i] += (target_elev - self.card_elevations[i]) * min(1.0, dt * 18.0)

        self.targeted_enemy = self._get_enemy_under_pos(mouse_pos) if self.state.targeting_active else None

    def draw(self, surface):
        # 1. Dark Gothic Background
        surface.fill((16, 13, 22))

        # Ambient Dungeon Arches & Torch Glow
        self._draw_dungeon_background(surface)

        # Ambient floating motes
        for m in self.ambient_motes:
            alpha = int(120 * (m[4] / 5.0))
            mote_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(mote_surf, (200, 190, 225, alpha), (3, 3), int(m[5]))
            surface.blit(mote_surf, (int(m[0] - 3), int(m[1] - 3)))

        # Top Bar
        draw_top_bar(surface, self.state.player, self.state.turn)

        # 2. Combat Action Banner (Upper Center)
        if self.state.combat_banner:
            self._draw_combat_banner(surface, self.state.combat_banner)

        # 3. Draw Player
        self.state.player.draw(surface)
        px = int(self.state.player.x + self.state.player.lunge_x)
        self._draw_styled_health_bar(
            surface,
            px,
            self.state.player.y + self.state.player.height + 12,
            self.state.player.width,
            20,
            self.state.player.hp,
            self.state.player.max_hp,
            self.state.player.block,
            ghost_hp=self.ghost_hp.get(self.state.player)
        )
        self._draw_status_badges(surface, self.state.player, px, self.state.player.y + self.state.player.height + 36)

        # 4. Draw Enemies
        for enemy in self.state.enemies:
            if enemy.is_alive():
                ex = int(enemy.x + enemy.lunge_x)

                # Active attacker highlight during enemy turn
                if self.state.phase == "enemy_turn" and enemy == self.state.acting_enemy:
                    act_rect = pygame.Rect(ex - 6, enemy.y - 6, enemy.width + 12, enemy.height + 12)
                    pygame.draw.rect(surface, (255, 90, 80), act_rect, width=2, border_radius=14)

                enemy.draw(surface)
                self._draw_styled_health_bar(
                    surface,
                    ex,
                    enemy.y + enemy.height + 12,
                    enemy.width,
                    20,
                    enemy.hp,
                    enemy.max_hp,
                    enemy.block,
                    ghost_hp=self.ghost_hp.get(enemy)
                )
                self._draw_status_badges(surface, enemy, ex, enemy.y + enemy.height + 36)

                # Animated Targeting Reticle over targeted enemy
                if enemy == self.targeted_enemy:
                    self._draw_targeting_reticle(surface, ex, enemy.y, enemy.width, enemy.height)

        # 5. Slay the Spire Style Energy Orb (Bottom-Left)
        self._draw_energy_orb(surface)

        # 6. Deck / Discard / Exhaust Indicators & Turn Stats
        draw_txt = FONTS['bold'].render(f"Draw: {len(self.state.player.draw_pile)}", True, (190, 180, 210))
        surface.blit(draw_txt, (35, 642))

        disc_txt = FONTS['bold'].render(f"Discard: {len(self.state.player.discard_pile)}", True, (190, 180, 210))
        surface.blit(disc_txt, (1125, 642))

        exh_txt = FONTS['small'].render(f"Exhaust: {len(self.state.player.exhaust_pile)}", True, (150, 140, 170))
        surface.blit(exh_txt, (1125, 670))

        combo_str = f"Combos: {self.state.cards_played_this_turn} Played ({self.state.attacks_played_this_turn} Attacks)"
        combo_txt = FONTS['small'].render(combo_str, True, (255, 215, 120))
        surface.blit(combo_txt, (35, 670))

        # 7. End Turn Button
        self.end_turn_btn.draw(surface)

        # 8. Draw Cards in Hand
        card_rects = self._get_hand_card_rects()
        for idx, (rect, card) in enumerate(card_rects):
            if self.state.targeting_active and card == self.state.selected_card:
                continue
            is_hover = (idx == self.hovered_card_idx)
            is_playable = self.state.can_play_card(card)
            eff_cost = self.state.get_card_cost(card)
            draw_card(surface, card, rect.x, rect.y, is_hover, is_playable, cost_override=eff_cost)

        # 9. Targeting Bezier Arrow
        if self.state.targeting_active and self.drag_start_pos:
            mouse_pos = pygame.mouse.get_pos()
            draw_targeting_arrow(surface, self.drag_start_pos, mouse_pos)

        # 10. Particles, Shockwaves & Damage Popups
        self.state.particle_mgr.draw(surface, FONTS['damage'])

    def _draw_targeting_reticle(self, surface, x, y, width, height):
        cx = x + width // 2
        cy = y + height // 2
        t = self.anim_time * 6.0
        pulse = math.sin(t) * 4
        rad = max(24, int(min(width, height) * 0.45 + pulse))

        # Glowing target ring
        ret_surf = pygame.Surface((rad * 2 + 20, rad * 2 + 20), pygame.SRCALPHA)
        center = (rad + 10, rad + 10)
        pygame.draw.circle(ret_surf, (255, 60, 60, 70), center, rad + 6)
        pygame.draw.circle(ret_surf, (255, 220, 80, 200), center, rad, width=2)
        # Inner dot
        pygame.draw.circle(ret_surf, (255, 240, 100), center, 3)

        # Rotating corner tick marks
        angle = self.anim_time * 2.5
        for i in range(4):
            a = angle + i * (math.pi / 2)
            p1_x = center[0] + math.cos(a) * (rad - 6)
            p1_y = center[1] + math.sin(a) * (rad - 6)
            p2_x = center[0] + math.cos(a) * (rad + 6)
            p2_y = center[1] + math.sin(a) * (rad + 6)
            pygame.draw.line(ret_surf, (255, 220, 80), (p1_x, p1_y), (p2_x, p2_y), 2)

        surface.blit(ret_surf, (cx - center[0], cy - center[1]))

    def _draw_dungeon_background(self, surface):
        # Wall torches ambient radial light
        for tx in (80, 1200):
            glow_surf = pygame.Surface((180, 180), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 140, 30, 35), (90, 90), 85)
            pygame.draw.circle(glow_surf, (255, 200, 60, 50), (90, 90), 45)
            surface.blit(glow_surf, (tx - 90, 240 - 90))

            # Torch bracket & flame
            pygame.draw.rect(surface, (60, 45, 40), (tx - 4, 235, 8, 25), border_radius=2)
            pygame.draw.circle(surface, (255, 160, 40), (tx, 232), 8)
            pygame.draw.circle(surface, (255, 240, 120), (tx, 230), 4)

        # Sparks
        for p in self.torch_particles:
            alpha = int(255 * (p[4] / 0.6))
            s_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, (255, 200, 60, max(0, min(255, alpha))), (2, 2), 2)
            surface.blit(s_surf, (int(p[0]), int(p[1])))

        # Gothic Flagstone Floor dividing line & perspective lines
        pygame.draw.line(surface, (55, 45, 68), (0, 480), (1280, 480), 2)
        for fx in range(160, 1200, 240):
            pygame.draw.line(surface, (35, 28, 45), (fx, 480), (fx - 60, 720), 1)

    def _draw_combat_banner(self, surface, text):
        banner_w = 640
        banner_h = 44
        bx = 640 - banner_w // 2
        by = 85

        banner_rect = pygame.Rect(bx, by, banner_w, banner_h)
        # Obsidian fill with brass border
        pygame.draw.rect(surface, (24, 18, 30), banner_rect, border_radius=8)
        pygame.draw.rect(surface, (220, 185, 90), banner_rect, width=2, border_radius=8)

        rendered = FONTS['medium'].render(text, True, (255, 235, 160))
        surface.blit(rendered, rendered.get_rect(center=banner_rect.center))

    def _draw_energy_orb(self, surface):
        orb_center = (90, 580)
        # Outer Brass Gear/Ring
        pygame.draw.circle(surface, (25, 20, 32), orb_center, 44)
        pygame.draw.circle(surface, (190, 145, 65), orb_center, 42, 3)

        # Fiery Energy Sphere
        pygame.draw.circle(surface, COLOR_ENERGY_ORB, orb_center, 38)
        # Glowing inner highlight
        pygame.draw.circle(surface, (255, 120, 90), (orb_center[0] - 8, orb_center[1] - 8), 16)

        energy_str = f"{self.state.player.energy}/{self.state.player.max_energy}"
        txt = FONTS['huge'].render(energy_str, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=orb_center))

    def _draw_styled_health_bar(self, surface, x, y, width, height, current_hp, max_hp, block=0, ghost_hp=None):
        # Background
        pygame.draw.rect(surface, COLOR_HEALTH_BG, (x, y, width, height), border_radius=5)

        # Delayed Ghost Damage Bar (amber/yellow trailing bar)
        if ghost_hp is not None and ghost_hp > current_hp:
            ghost_ratio = max(0.0, min(1.0, ghost_hp / max(1, max_hp)))
            ghost_w = int(width * ghost_ratio)
            if ghost_w > 0:
                pygame.draw.rect(surface, (230, 160, 45), (x, y, ghost_w, height), border_radius=5)

        # HP Fill (crimson red)
        ratio = max(0.0, min(1.0, current_hp / max(1, max_hp)))
        hp_w = int(width * ratio)
        if hp_w > 0:
            pygame.draw.rect(surface, COLOR_HEALTH_RED, (x, y, hp_w, height), border_radius=5)

        # Inner border
        pygame.draw.rect(surface, (80, 55, 90), (x, y, width, height), width=1, border_radius=5)

        # Superimposed Shield if Block > 0
        if block > 0:
            shield_size = 24
            sx = x - shield_size // 2 - 2
            sy = y + (height - shield_size) // 2
            pygame.draw.polygon(surface, COLOR_BLOCK_BLUE, [
                (sx + shield_size // 2, sy),
                (sx + shield_size, sy + shield_size // 3),
                (sx + shield_size // 2, sy + shield_size),
                (sx, sy + shield_size // 3)
            ])
            pygame.draw.polygon(surface, (255, 255, 255), [
                (sx + shield_size // 2, sy),
                (sx + shield_size, sy + shield_size // 3),
                (sx + shield_size // 2, sy + shield_size),
                (sx, sy + shield_size // 3)
            ], 2)
            blk_txt = FONTS['bold'].render(str(block), True, (255, 255, 255))
            surface.blit(blk_txt, blk_txt.get_rect(center=(sx + shield_size // 2, sy + shield_size // 2)))

        # HP Text
        hp_str = f"{current_hp}/{max_hp}"
        txt = FONTS['small'].render(hp_str, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=(x + width // 2, y + height // 2)))

    def _draw_status_badges(self, surface, entity, x, y):
        sx = x
        for status_name, amount in entity.statuses.statuses.items():
            if amount <= 0:
                continue
            badge_rect = pygame.Rect(sx, y, 22, 20)
            bg_col = (140, 40, 50) if status_name in ("Vulnerable", "Weak", "Poison") else (40, 120, 70)
            pygame.draw.rect(surface, bg_col, badge_rect, border_radius=4)
            letter = status_name[0]
            rendered = FONTS['small'].render(f"{letter}{amount}", True, (255, 255, 255))
            surface.blit(rendered, rendered.get_rect(center=badge_rect.center))
            sx += 26
