"""
Map View: Interactive branching dungeon map with multi-act vertical scrolling,
continuous viewport navigation, act preview inspection, and smooth animations.
"""
import math
import pygame
from systems.map_generator import DungeonMap, MapNode, NodeType
from engine.ui import draw_top_bar
from engine.sound import play_sfx
from settings import (
    COLOR_BG_DARK, COLOR_TEXT_LIGHT, COLOR_TEXT_GOLD, FONTS
)

NODE_COLORS = {
    NodeType.MONSTER: (210, 50, 60),
    NodeType.ELITE: (230, 40, 140),
    NodeType.EVENT: (70, 160, 240),
    NodeType.REST: (240, 140, 40),
    NodeType.SHOP: (240, 215, 60),
    NodeType.BOSS: (190, 30, 40)
}

NODE_SYMBOLS = {
    NodeType.MONSTER: "M",
    NodeType.ELITE: "E",
    NodeType.EVENT: "?",
    NodeType.REST: "R",
    NodeType.SHOP: "$",
    NodeType.BOSS: "B"
}

FLOOR_SPACING = 54
ACT_GAP = 140
ACT_STRIDE = 9 * FLOOR_SPACING + ACT_GAP  # 486 + 140 = 626 pixels per act

class MapView:
    def __init__(self, dungeon_map: DungeonMap, player):
        self.dungeon_map = dungeon_map
        self.player = player
        self.hovered_node = None
        self.hovered_act = 1
        self.save_btn_rect = pygame.Rect(1005, 10, 120, 32)
        self.deck_btn_rect = pygame.Rect(1140, 10, 110, 32)

        # Scrolling mechanics
        self.total_acts = max(3, self.dungeon_map.act)
        self.max_scroll = max(0, (self.total_acts - 1) * ACT_STRIDE + 60)
        self.min_scroll = 0.0

        # Center on player's current act and floor initially
        initial_offset = (self.dungeon_map.act - 1) * ACT_STRIDE
        if self.dungeon_map.current_floor > 3:
            initial_offset += (self.dungeon_map.current_floor - 2) * FLOOR_SPACING
        self.scroll_offset = float(max(0, min(self.max_scroll, initial_offset)))
        self.target_scroll_offset = self.scroll_offset

        # Dragging state
        self.is_dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0.0
        self.has_dragged = False

        # Pulse animation timer
        self.anim_time = 0.0

    def _get_act_pills_rects(self) -> list[tuple[int, pygame.Rect, str]]:
        """Returns list of (act_id, rect, label) for top navigation pills."""
        total_acts = max(3, self.dungeon_map.act)
        pill_w = 80
        spacing = 8
        total_pills = total_acts + 1
        total_w = total_acts * pill_w + (total_acts - 1) * spacing + 12 + 96
        start_x = 640 - total_w / 2

        results = []
        cur_x = start_x
        for a in range(1, total_acts + 1):
            rect = pygame.Rect(int(cur_x), 46, pill_w, 24)
            roman = ["I", "II", "III", "IV", "V", "VI"][a - 1] if a <= 6 else str(a)
            results.append((a, rect, f"ACT {roman}"))
            cur_x += pill_w + spacing

        cur_x += 4
        current_rect = pygame.Rect(int(cur_x), 46, 96, 24)
        results.append((-1, current_rect, "CURRENT"))
        return results

    def handle_event(self, event, mouse_pos) -> tuple[str, MapNode]:
        # Mouse Wheel for smooth Act and Floor scrolling
        if event.type == pygame.MOUSEWHEEL:
            # Scroll up reveals higher acts / floors
            scroll_delta = event.y * 70
            self.target_scroll_offset = max(self.min_scroll, min(self.max_scroll, self.target_scroll_offset + scroll_delta))
            return "none", None

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check Save & Quit button
            if self.save_btn_rect.collidepoint(event.pos):
                play_sfx('click', 0.5)
                return "save_and_quit", None

            # Check deck button
            if self.deck_btn_rect.collidepoint(event.pos):
                play_sfx('click', 0.5)
                return "open_deck", None

            # Check Act Pills
            for act_id, rect, _ in self._get_act_pills_rects():
                if rect.collidepoint(event.pos):
                    play_sfx('click', 0.5)
                    if act_id == -1:
                        # Scroll to current floor
                        cur_target = (self.dungeon_map.act - 1) * ACT_STRIDE
                        if self.dungeon_map.current_floor > 3:
                            cur_target += (self.dungeon_map.current_floor - 2) * FLOOR_SPACING
                        self.target_scroll_offset = max(self.min_scroll, min(self.max_scroll, cur_target))
                    else:
                        self.target_scroll_offset = max(self.min_scroll, min(self.max_scroll, (act_id - 1) * ACT_STRIDE))
                    return "none", None

            # Check node click
            node, node_act = self._get_node_at_pos(event.pos)
            if node and node_act == self.dungeon_map.act and node.available:
                if self.dungeon_map.select_node(node):
                    play_sfx('card_draw', 0.6)
                    return "enter_node", node
            elif node and node_act != self.dungeon_map.act:
                play_sfx('debuff', 0.4)
                return "none", None

            # If clicked on empty map background, begin drag panning
            if 44 <= event.pos[1] <= 675:
                self.is_dragging = True
                self.drag_start_y = event.pos[1]
                self.drag_start_scroll = self.target_scroll_offset
                self.has_dragged = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                delta_y = event.pos[1] - self.drag_start_y
                if abs(delta_y) > 3:
                    self.has_dragged = True
                # Dragging down moves content down (scrolls down in world / lower floors)
                self.target_scroll_offset = max(self.min_scroll, min(self.max_scroll, self.drag_start_scroll + delta_y))
                self.scroll_offset = self.target_scroll_offset

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_sfx('click', 0.5)
                return "save_and_quit", None
            elif event.key in (pygame.K_UP, pygame.K_PAGEUP):
                self.target_scroll_offset = max(self.min_scroll, min(self.max_scroll, self.target_scroll_offset + 140))
            elif event.key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
                self.target_scroll_offset = max(self.min_scroll, min(self.max_scroll, self.target_scroll_offset - 140))
            elif event.key == pygame.K_HOME:
                self.target_scroll_offset = self.max_scroll
            elif event.key == pygame.K_END:
                self.target_scroll_offset = self.min_scroll

        return "none", None

    def update(self, dt, mouse_pos):
        self.anim_time += dt

        # Smooth camera glide
        if not self.is_dragging:
            self.scroll_offset += (self.target_scroll_offset - self.scroll_offset) * min(1.0, dt * 14.0)
            if abs(self.target_scroll_offset - self.scroll_offset) < 0.2:
                self.scroll_offset = self.target_scroll_offset

        node, act = self._get_node_at_pos(mouse_pos)
        self.hovered_node = node
        self.hovered_act = act

    def _get_node_position(self, floor_idx: int, node_idx: int, total_nodes: int, act: int = None):
        """Calculates screen (x, y) for any floor node in any Act accounting for current scroll offset."""
        if act is None:
            act = self.dungeon_map.act
        world_y = (act - 1) * ACT_STRIDE + floor_idx * FLOOR_SPACING
        screen_y = 610 - int(world_y - self.scroll_offset)

        # Horizontal spacing
        spacing = 180
        total_w = (total_nodes - 1) * spacing
        start_x = 640 - total_w / 2
        x = start_x + node_idx * spacing
        return int(x), int(screen_y)

    def _get_node_at_pos(self, pos) -> tuple[MapNode | None, int]:
        """Finds node under mouse pointer across visible acts."""
        if pos[1] < 45 or pos[1] > 675:
            return None, self.dungeon_map.act

        total_acts = max(3, self.dungeon_map.act)
        for act in range(1, total_acts + 1):
            floors = self.dungeon_map.get_act_floors(act)
            for f_idx, floor_nodes in enumerate(floors):
                for n_idx, node in enumerate(floor_nodes):
                    x, y = self._get_node_position(f_idx, n_idx, len(floor_nodes), act=act)
                    if 25 <= y <= 695:
                        dist = ((pos[0] - x)**2 + (pos[1] - y)**2)**0.5
                        radius = 26 if node.node_type == NodeType.BOSS else 20
                        if dist <= radius + 3:
                            return node, act
        return None, self.dungeon_map.act

    def draw(self, surface):
        # 1. Atmospheric Background based on Act currently centered in viewport
        total_acts = max(3, self.dungeon_map.act)
        view_act = min(total_acts, max(1, int((self.scroll_offset + 300) / ACT_STRIDE) + 1))

        if view_act == 2:
            surface.fill((28, 14, 18))
        elif view_act == 3:
            surface.fill((14, 18, 32))
        elif view_act >= 4:
            surface.fill((24, 12, 28))
        else:
            surface.fill(COLOR_BG_DARK)

        # 2. Map Viewport with strict clipping between Top Bar (y=44) and Legend (y=675)
        viewport_rect = pygame.Rect(0, 44, 1280, 631)
        surface.set_clip(viewport_rect)

        # Draw Act Gateway banners and Connections across all acts
        for act in range(1, total_acts + 1):
            floors = self.dungeon_map.get_act_floors(act)
            is_active_act = (act == self.dungeon_map.act)
            is_past_act = (act < self.dungeon_map.act)

            # Draw Gateway separator banner between acts
            if act > 1:
                banner_world_y = (act - 1) * ACT_STRIDE - ACT_GAP // 2
                banner_screen_y = 610 - int(banner_world_y - self.scroll_offset)
                if -40 <= banner_screen_y <= 730:
                    b_rect = pygame.Rect(320, banner_screen_y - 18, 640, 36)
                    # Stone banner with gold/silver accents
                    border_col = (215, 175, 75) if is_active_act else (90, 75, 110)
                    pygame.draw.rect(surface, (24, 20, 32), b_rect, border_radius=6)
                    pygame.draw.rect(surface, border_col, b_rect, width=1, border_radius=6)
                    
                    banner_title = f"— GATEWAY TO {self.dungeon_map.get_act_title(act)} —"
                    b_txt = FONTS['bold'].render(banner_title, True, (245, 225, 160) if is_active_act else (160, 150, 180))
                    surface.blit(b_txt, b_txt.get_rect(center=b_rect.center))

            # Draw Connections for this act
            for f_idx in range(len(floors) - 1):
                curr_floor = floors[f_idx]
                next_floor = floors[f_idx + 1]

                for n_idx, node in enumerate(curr_floor):
                    x1, y1 = self._get_node_position(f_idx, n_idx, len(curr_floor), act=act)
                    for target_idx in node.connections:
                        if target_idx < len(next_floor):
                            x2, y2 = self._get_node_position(f_idx + 1, target_idx, len(next_floor), act=act)
                            # Culling check
                            if (20 <= y1 <= 700) or (20 <= y2 <= 700):
                                if is_active_act:
                                    line_col = (130, 95, 170) if (node.visited and next_floor[target_idx].available) else (50, 42, 60)
                                    line_w = 3 if (node.visited and next_floor[target_idx].available) else 2
                                elif is_past_act:
                                    line_col = (160, 140, 90) if (node.visited and next_floor[target_idx].visited) else (40, 35, 50)
                                    line_w = 2
                                else:
                                    # Future Act preview
                                    line_col = (60, 52, 72)
                                    line_w = 1
                                pygame.draw.line(surface, line_col, (x1, y1), (x2, y2), line_w)

            # Draw Nodes for this act
            for f_idx, floor_nodes in enumerate(floors):
                for n_idx, node in enumerate(floor_nodes):
                    x, y = self._get_node_position(f_idx, n_idx, len(floor_nodes), act=act)
                    if 20 <= y <= 700:
                        color = NODE_COLORS[node.node_type]
                        radius = 26 if node.node_type == NodeType.BOSS else 20

                        if is_active_act:
                            # Current Act: active interactive nodes
                            if node.available:
                                # Pulsing glowing gold halo
                                pulse = 1.0 + 0.15 * pygame.math.clamp(math.sin(self.anim_time * 5.0), -1.0, 1.0)
                                glow_r = int((radius + 5) * pulse)
                                pygame.draw.circle(surface, (255, 235, 120), (x, y), glow_r, 2)
                            elif node.visited:
                                pygame.draw.circle(surface, (150, 150, 150), (x, y), radius + 3, 1)

                            fill_color = color if (node.available or node.visited) else (38, 32, 45)
                            sym_color = (255, 255, 255) if (node.available or node.visited) else (115, 105, 125)
                        elif is_past_act:
                            # Past Act: historical journey record
                            if node.visited:
                                pygame.draw.circle(surface, (220, 190, 90), (x, y), radius + 3, 2)
                                fill_color = color
                                sym_color = (255, 255, 255)
                            else:
                                fill_color = (30, 26, 36)
                                sym_color = (80, 75, 90)
                        else:
                            # Future Act: Preview mode
                            fill_color = (35, 30, 44)
                            # Draw subtle jewel ring
                            pygame.draw.circle(surface, (*color[:3], 140), (x, y), radius + 1, 1)
                            sym_color = color

                        # Boss nodes have majestic double border
                        if node.node_type == NodeType.BOSS:
                            boss_glow = (255, 90, 70) if is_active_act else (180, 70, 90)
                            pygame.draw.circle(surface, boss_glow, (x, y), radius + 3, 1)

                        pygame.draw.circle(surface, fill_color, (x, y), radius)
                        pygame.draw.circle(surface, (20, 16, 26), (x, y), radius, 2)

                        # Icon symbol
                        symbol = NODE_SYMBOLS[node.node_type]
                        font = FONTS['medium'] if node.node_type == NodeType.BOSS else FONTS['bold']
                        txt = font.render(symbol, True, sym_color)
                        surface.blit(txt, txt.get_rect(center=(x, y)))

        # Pinnacle Banner at very top of the spire
        pinnacle_world_y = total_acts * ACT_STRIDE - ACT_GAP // 2
        pinnacle_y = 610 - int(pinnacle_world_y - self.scroll_offset)
        if -40 <= pinnacle_y <= 730:
            pin_rect = pygame.Rect(340, pinnacle_y - 18, 600, 36)
            pygame.draw.rect(surface, (20, 14, 28), pin_rect, border_radius=6)
            pygame.draw.rect(surface, (255, 70, 90), pin_rect, width=1, border_radius=6)
            pin_txt = FONTS['bold'].render("💀 THE SPIRE PINNACLE: MALAKOR'S SANCTUM 💀", True, (255, 140, 140))
            surface.blit(pin_txt, pin_txt.get_rect(center=pin_rect.center))

        # Reset clipping for UI layer
        surface.set_clip(None)

        # 3. Top Bar with cumulative floor
        cumul_floor = self.dungeon_map.get_cumulative_floor() if hasattr(self.dungeon_map, 'get_cumulative_floor') else self.dungeon_map.current_floor + 1
        draw_top_bar(surface, self.player, cumul_floor)

        # 4. Save & Quit Button in Top Bar
        mouse_pos = pygame.mouse.get_pos()
        is_save_hov = self.save_btn_rect.collidepoint(mouse_pos)
        save_bg = (105, 32, 45) if is_save_hov else (68, 25, 36)
        save_border = (210, 75, 90) if is_save_hov else (130, 48, 62)
        pygame.draw.rect(surface, save_bg, self.save_btn_rect, border_radius=6)
        pygame.draw.rect(surface, save_border, self.save_btn_rect, width=1, border_radius=6)
        s_txt = FONTS['small'].render("Save & Quit", True, (245, 230, 235))
        surface.blit(s_txt, s_txt.get_rect(center=self.save_btn_rect.center))

        # 5. Deck View Button in Top Bar
        is_deck_hov = self.deck_btn_rect.collidepoint(mouse_pos)
        deck_bg = (68, 52, 88) if is_deck_hov else (50, 40, 65)
        pygame.draw.rect(surface, deck_bg, self.deck_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (140, 120, 170), self.deck_btn_rect, width=1, border_radius=6)
        d_txt = FONTS['small'].render(f"Deck ({len(self.player.deck)})", True, COLOR_TEXT_LIGHT)
        surface.blit(d_txt, d_txt.get_rect(center=self.deck_btn_rect.center))

        # 6. Act Navigation Pills (Quick-jump across Acts)
        for act_id, rect, label in self._get_act_pills_rects():
            is_active_view = (act_id == view_act) or (act_id == -1 and abs(self.scroll_offset - ((self.dungeon_map.act - 1) * ACT_STRIDE)) < 150)
            is_hov = rect.collidepoint(mouse_pos)

            if is_active_view:
                pill_bg = (90, 68, 120) if is_hov else (70, 52, 95)
                pill_border = (255, 225, 110)
                pill_text_col = (255, 245, 210)
            else:
                pill_bg = (52, 40, 68) if is_hov else (34, 26, 45)
                pill_border = (120, 100, 145) if is_hov else (70, 60, 85)
                pill_text_col = (200, 190, 215) if is_hov else (145, 135, 160)

            pygame.draw.rect(surface, pill_bg, rect, border_radius=5)
            pygame.draw.rect(surface, pill_border, rect, width=1, border_radius=5)
            p_txt = FONTS['small'].render(label, True, pill_text_col)
            surface.blit(p_txt, p_txt.get_rect(center=rect.center))

        # 7. Act Title Banner for the Act in View
        act_title = self.dungeon_map.get_act_title(view_act)
        title_txt = FONTS['title'].render(act_title, True, (245, 225, 160))
        surface.blit(title_txt, title_txt.get_rect(center=(640, 88)))

        # 8. Interactive Scrollbar on the right edge
        if self.max_scroll > 0:
            track_rect = pygame.Rect(1266, 80, 6, 580)
            pygame.draw.rect(surface, (30, 24, 38), track_rect, border_radius=3)
            # Thumb
            thumb_h = max(30, int(580 * (600 / (self.max_scroll + 600))))
            thumb_ratio = 1.0 - (self.scroll_offset / self.max_scroll)
            thumb_y = track_rect.y + int((track_rect.height - thumb_h) * thumb_ratio)
            thumb_rect = pygame.Rect(1265, thumb_y, 8, thumb_h)
            pygame.draw.rect(surface, (170, 140, 210), thumb_rect, border_radius=4)

        # 9. Bottom Legend & Helpful Controls Prompt
        legend_y = 692
        legend_items = [
            ("M - Monster", NODE_COLORS[NodeType.MONSTER]),
            ("E - Elite", NODE_COLORS[NodeType.ELITE]),
            ("? - Mystery", NODE_COLORS[NodeType.EVENT]),
            ("R - Rest", NODE_COLORS[NodeType.REST]),
            ("$ - Shop", NODE_COLORS[NodeType.SHOP]),
            ("B - Boss", NODE_COLORS[NodeType.BOSS]),
        ]
        lx = 120
        for name, col in legend_items:
            pygame.draw.circle(surface, col, (lx, legend_y), 7)
            t = FONTS['small'].render(name, True, (190, 185, 205))
            surface.blit(t, (lx + 12, legend_y - 8))
            lx += 135

        # Scroll hint indicator
        hint_txt = FONTS['small'].render("Scroll Wheel / Drag: View Other Acts", True, (215, 195, 120))
        surface.blit(hint_txt, (1000, legend_y - 8))

        # 10. Hovered Node Inspection Tooltip
        if self.hovered_node is not None:
            node = self.hovered_node
            act = self.hovered_act
            is_active = (act == self.dungeon_map.act)
            roman = ["I", "II", "III", "IV", "V", "VI"][act - 1] if act <= 6 else str(act)

            if is_active:
                if node.available:
                    status_desc = "Available (Click to Enter)"
                elif node.visited:
                    status_desc = "Completed"
                else:
                    status_desc = "Not on chosen path"
            elif act > self.dungeon_map.act:
                status_desc = f"Locked (Reach Act {roman})"
            else:
                status_desc = "Past Act (Completed)"

            type_name = node.node_type.value
            tooltip_str = f"ACT {roman} | Floor {node.floor + 1}: {type_name} — {status_desc}"

            tt_surf = FONTS['small'].render(tooltip_str, True, (255, 245, 220))
            tw, th = tt_surf.get_size()
            tx = max(10, min(1270 - tw - 16, mouse_pos[0] + 16))
            ty = max(50, min(670 - th - 10, mouse_pos[1] - 30))

            tip_bg = pygame.Rect(tx, ty, tw + 16, th + 10)
            pygame.draw.rect(surface, (20, 16, 26), tip_bg, border_radius=5)
            pygame.draw.rect(surface, (190, 160, 90) if is_active else (110, 90, 130), tip_bg, width=1, border_radius=5)
            surface.blit(tt_surf, (tx + 8, ty + 5))
