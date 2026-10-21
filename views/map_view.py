"""
Map View: Interactive branching dungeon map.
"""
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

class MapView:
    def __init__(self, dungeon_map: DungeonMap, player):
        self.dungeon_map = dungeon_map
        self.player = player
        self.hovered_node = None
        self.save_btn_rect = pygame.Rect(1005, 10, 120, 32)
        self.deck_btn_rect = pygame.Rect(1140, 10, 110, 32)

    def handle_event(self, event, mouse_pos) -> tuple[str, MapNode]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check Save & Quit button
            if self.save_btn_rect.collidepoint(event.pos):
                play_sfx('click', 0.5)
                return "save_and_quit", None

            # Check deck button
            if self.deck_btn_rect.collidepoint(event.pos):
                play_sfx('click', 0.5)
                return "open_deck", None

            # Check node click
            node = self._get_node_at_pos(event.pos)
            if node and node.available:
                if self.dungeon_map.select_node(node):
                    play_sfx('card_draw', 0.6)
                    return "enter_node", node

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            play_sfx('click', 0.5)
            return "save_and_quit", None

        return "none", None

    def update(self, dt, mouse_pos):
        self.hovered_node = self._get_node_at_pos(mouse_pos)

    def _get_node_position(self, floor_idx: int, node_idx: int, total_nodes: int):
        # Floors flow from bottom to top like Slay the Spire!
        # Floor 0 at bottom (y=620), Floor 9/Boss at top (y=100)
        y = 610 - floor_idx * 52

        # Horizontal spacing
        spacing = 180
        total_w = (total_nodes - 1) * spacing
        start_x = 640 - total_w / 2
        x = start_x + node_idx * spacing
        return int(x), int(y)

    def _get_node_at_pos(self, pos):
        for f_idx, floor_nodes in enumerate(self.dungeon_map.floors):
            for n_idx, node in enumerate(floor_nodes):
                x, y = self._get_node_position(f_idx, n_idx, len(floor_nodes))
                dist = ((pos[0] - x)**2 + (pos[1] - y)**2)**0.5
                if dist <= 22:
                    return node
        return None

    def draw(self, surface):
        # Act-specific atmospheric background tint
        act = getattr(self.dungeon_map, 'act', 1)
        if act == 2:
            surface.fill((25, 12, 15))
        elif act == 3:
            surface.fill((12, 15, 28))
        elif act >= 4:
            surface.fill((22, 12, 26))
        else:
            surface.fill(COLOR_BG_DARK)

        # Top Bar with cumulative floor
        cumul_floor = self.dungeon_map.get_cumulative_floor() if hasattr(self.dungeon_map, 'get_cumulative_floor') else self.dungeon_map.current_floor + 1
        draw_top_bar(surface, self.player, cumul_floor)

        # Save & Quit Button in Top Bar
        mouse_pos = pygame.mouse.get_pos()
        is_save_hov = self.save_btn_rect.collidepoint(mouse_pos)
        save_bg = (105, 32, 45) if is_save_hov else (68, 25, 36)
        save_border = (210, 75, 90) if is_save_hov else (130, 48, 62)
        pygame.draw.rect(surface, save_bg, self.save_btn_rect, border_radius=6)
        pygame.draw.rect(surface, save_border, self.save_btn_rect, width=1, border_radius=6)
        s_txt = FONTS['small'].render("Save & Quit", True, (245, 230, 235))
        surface.blit(s_txt, s_txt.get_rect(center=self.save_btn_rect.center))

        # Deck View Button in Top Bar
        is_deck_hov = self.deck_btn_rect.collidepoint(mouse_pos)
        deck_bg = (68, 52, 88) if is_deck_hov else (50, 40, 65)
        pygame.draw.rect(surface, deck_bg, self.deck_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (140, 120, 170), self.deck_btn_rect, width=1, border_radius=6)
        d_txt = FONTS['small'].render(f"Deck ({len(self.player.deck)})", True, COLOR_TEXT_LIGHT)
        surface.blit(d_txt, d_txt.get_rect(center=self.deck_btn_rect.center))

        # Act Title Banner
        act_title = self.dungeon_map.get_act_title() if hasattr(self.dungeon_map, 'get_act_title') else "MAP OF THE CATACOMBS"
        title_txt = FONTS['title'].render(act_title, True, (240, 220, 160))
        surface.blit(title_txt, title_txt.get_rect(center=(640, 75)))

        # Draw Connections (lines between adjacent floor nodes)
        for f_idx in range(len(self.dungeon_map.floors) - 1):
            curr_floor = self.dungeon_map.floors[f_idx]
            next_floor = self.dungeon_map.floors[f_idx + 1]

            for n_idx, node in enumerate(curr_floor):
                x1, y1 = self._get_node_position(f_idx, n_idx, len(curr_floor))
                for target_idx in node.connections:
                    if target_idx < len(next_floor):
                        x2, y2 = self._get_node_position(f_idx + 1, target_idx, len(next_floor))
                        line_col = (110, 80, 140) if (node.visited and next_floor[target_idx].available) else (50, 42, 60)
                        pygame.draw.line(surface, line_col, (x1, y1), (x2, y2), 2)

        # Draw Nodes
        for f_idx, floor_nodes in enumerate(self.dungeon_map.floors):
            for n_idx, node in enumerate(floor_nodes):
                x, y = self._get_node_position(f_idx, n_idx, len(floor_nodes))
                color = NODE_COLORS[node.node_type]
                radius = 20 if node.node_type != NodeType.BOSS else 26

                # Outer ring if available or visited
                if node.available:
                    glow_color = (255, 240, 120)
                    pygame.draw.circle(surface, glow_color, (x, y), radius + 5, 2)
                elif node.visited:
                    pygame.draw.circle(surface, (140, 140, 140), (x, y), radius + 3, 1)

                # Node circle
                fill_color = color if (node.available or node.visited) else (40, 35, 48)
                pygame.draw.circle(surface, fill_color, (x, y), radius)
                pygame.draw.circle(surface, (20, 16, 26), (x, y), radius, 2)

                # Icon symbol
                symbol = NODE_SYMBOLS[node.node_type]
                sym_color = (255, 255, 255) if (node.available or node.visited) else (100, 95, 110)
                font = FONTS['medium'] if node.node_type == NodeType.BOSS else FONTS['bold']
                txt = font.render(symbol, True, sym_color)
                surface.blit(txt, txt.get_rect(center=(x, y)))

        # Legend at bottom
        legend_y = 680
        legend_items = [
            ("M - Monster", NODE_COLORS[NodeType.MONSTER]),
            ("E - Elite", NODE_COLORS[NodeType.ELITE]),
            ("? - Mystery", NODE_COLORS[NodeType.EVENT]),
            ("R - Rest", NODE_COLORS[NodeType.REST]),
            ("$ - Shop", NODE_COLORS[NodeType.SHOP]),
            ("B - Boss", NODE_COLORS[NodeType.BOSS]),
        ]
        lx = 220
        for name, col in legend_items:
            pygame.draw.circle(surface, col, (lx, legend_y), 7)
            t = FONTS['small'].render(name, True, (180, 175, 195))
            surface.blit(t, (lx + 12, legend_y - 8))
            lx += 150
