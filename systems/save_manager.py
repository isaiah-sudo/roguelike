"""
Save Manager System for Crypt of the Necrolord.
Handles serialization and deserialization of run progress across save slots.
"""
import os
import sys
import json
import inspect
from datetime import datetime
from typing import Optional, Any

import models.card as card_module
from models.card import Card, StrikeCard
import models.relic as relic_module
from models.relic import Relic
import models.potion as potion_module
from models.potion import Potion
from models.player import Player
from systems.map_generator import DungeonMap, MapNode, NodeType

NUM_SLOTS = 3

# Dynamically index all Card, Relic, and Potion classes by id_name
CARD_REGISTRY: dict[str, type[Card]] = {}
for _, cls in inspect.getmembers(card_module, inspect.isclass):
    if issubclass(cls, Card) and cls is not Card:
        try:
            sample = cls()
            CARD_REGISTRY[sample.id_name] = cls
        except Exception:
            pass

RELIC_REGISTRY: dict[str, type[Relic]] = {}
for _, cls in inspect.getmembers(relic_module, inspect.isclass):
    if issubclass(cls, Relic) and cls is not Relic:
        try:
            sample = cls()
            RELIC_REGISTRY[sample.id_name] = cls
        except Exception:
            pass

POTION_REGISTRY: dict[str, type[Potion]] = {}
for _, cls in inspect.getmembers(potion_module, inspect.isclass):
    if issubclass(cls, Potion) and cls is not Potion:
        try:
            sample = cls()
            POTION_REGISTRY[sample.id_name] = cls
        except Exception:
            pass


def get_save_dir() -> str:
    """Return the absolute path to the directory where save files are stored."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, "saves")
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def get_save_path(slot_id: int) -> str:
    return os.path.join(get_save_dir(), f"slot_{slot_id}.json")


def save_game(slot_id: int, player: Player, dungeon_map: DungeonMap, current_act: int,
              is_current_elite: bool = False, is_current_boss: bool = False) -> bool:
    """Safely saves the active run to the specified slot."""
    try:
        now = datetime.now()
        save_data = {
            "version": 1,
            "slot_id": slot_id,
            "timestamp": now.strftime("%b %d, %Y - %H:%M"),
            "saved_at_iso": now.isoformat(),
            "current_act": current_act,
            "is_current_elite": is_current_elite,
            "is_current_boss": is_current_boss,
            "player": {
                "char_id": player.char_id,
                "name": player.name,
                "class_title": getattr(player, 'class_title', ''),
                "hp": player.hp,
                "max_hp": player.max_hp,
                "gold": player.gold,
                "max_energy": getattr(player, 'max_energy', 3),
                "deck": [
                    {"id_name": c.id_name, "upgraded": getattr(c, 'upgraded', False)}
                    for c in player.deck
                ],
                "relics": [
                    {"id_name": r.id_name, "counter": getattr(r, 'counter', 0)}
                    for r in player.relics
                ],
                "potions": [
                    {"id_name": p.id_name} if p is not None else None
                    for p in player.potions
                ]
            },
            "dungeon_map": {
                "num_floors": dungeon_map.num_floors,
                "paths_per_floor": dungeon_map.paths_per_floor,
                "act": dungeon_map.act,
                "current_floor": dungeon_map.current_floor,
                "seed": getattr(dungeon_map, 'seed', 12345678),
                "act_title": dungeon_map.get_act_title() if hasattr(dungeon_map, 'get_act_title') else f"Act {current_act}",
                "cumulative_floor": dungeon_map.get_cumulative_floor() if hasattr(dungeon_map, 'get_cumulative_floor') else dungeon_map.current_floor + 1,
                "current_node": (
                    {"floor": dungeon_map.current_node.floor, "index": dungeon_map.current_node.index}
                    if getattr(dungeon_map, 'current_node', None) is not None else None
                ),
                "floors": [
                    [
                        {
                            "floor": node.floor,
                            "index": node.index,
                            "node_type": node.node_type.name,
                            "connections": list(node.connections),
                            "visited": node.visited,
                            "available": node.available
                        }
                        for node in fl
                    ]
                    for fl in dungeon_map.floors
                ],
                "act_maps": {
                    str(act_k): [
                        [
                            {
                                "floor": node.floor,
                                "index": node.index,
                                "node_type": node.node_type.name,
                                "connections": list(node.connections),
                                "visited": node.visited,
                                "available": node.available
                            }
                            for node in fl
                        ]
                        for fl in act_floors
                    ]
                    for act_k, act_floors in getattr(dungeon_map, 'act_maps', {}).items()
                }
            }
        }

        save_path = get_save_path(slot_id)
        tmp_path = save_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2)

        os.replace(tmp_path, save_path)
        return True
    except Exception as e:
        print(f"[SaveManager] Error saving game slot {slot_id}: {e}")
        return False


def load_game(slot_id: int) -> Optional[dict[str, Any]]:
    """Loads and reconstructs Player, DungeonMap, and game parameters from a save slot."""
    save_path = get_save_path(slot_id)
    if not os.path.exists(save_path):
        return None

    try:
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. Rebuild Player
        p_data = data["player"]
        char_id = p_data.get("char_id", "blood_knight")
        player = Player(char_id=char_id)
        player.hp = p_data.get("hp", player.hp)
        player.max_hp = p_data.get("max_hp", player.max_hp)
        player.gold = p_data.get("gold", player.gold)
        player.max_energy = p_data.get("max_energy", player.max_energy)

        # Rebuild Deck
        player.deck = []
        for c_info in p_data.get("deck", []):
            card_id = c_info.get("id_name", "strike")
            card_cls = CARD_REGISTRY.get(card_id, StrikeCard)
            card = card_cls()
            if c_info.get("upgraded", False):
                card.upgrade()
            player.deck.append(card)

        # Rebuild Relics
        player.relics = []
        for r_info in p_data.get("relics", []):
            relic_id = r_info.get("id_name")
            relic_cls = RELIC_REGISTRY.get(relic_id)
            if relic_cls:
                relic = relic_cls()
                relic.counter = r_info.get("counter", 0)
                player.relics.append(relic)

        # Rebuild Potions
        player.potions = []
        for pot_info in p_data.get("potions", []):
            if pot_info and pot_info.get("id_name"):
                pot_cls = POTION_REGISTRY.get(pot_info["id_name"])
                player.potions.append(pot_cls() if pot_cls else None)
            else:
                player.potions.append(None)
        while len(player.potions) < 3:
            player.potions.append(None)

        # 2. Rebuild DungeonMap
        m_data = data["dungeon_map"]
        dungeon_map = DungeonMap.__new__(DungeonMap)
        dungeon_map.num_floors = m_data.get("num_floors", 10)
        dungeon_map.paths_per_floor = m_data.get("paths_per_floor", 3)
        dungeon_map.act = m_data.get("act", data.get("current_act", 1))
        dungeon_map.current_floor = m_data.get("current_floor", 0)
        dungeon_map.seed = m_data.get("seed", 12345678)
        dungeon_map.floors = []
        dungeon_map.act_maps = {}

        for floor_nodes_data in m_data.get("floors", []):
            floor_nodes = []
            for n_info in floor_nodes_data:
                ntype_name = n_info.get("node_type", "MONSTER")
                ntype = NodeType[ntype_name] if ntype_name in NodeType.__members__ else NodeType.MONSTER
                node = MapNode(n_info["floor"], n_info["index"], ntype)
                node.connections = list(n_info.get("connections", []))
                node.visited = bool(n_info.get("visited", False))
                node.available = bool(n_info.get("available", False))
                floor_nodes.append(node)
            dungeon_map.floors.append(floor_nodes)

        # Reconstruct act_maps dictionary if saved
        for act_str, act_floors_data in m_data.get("act_maps", {}).items():
            act_num = int(act_str)
            if act_num == dungeon_map.act:
                dungeon_map.act_maps[act_num] = dungeon_map.floors
                continue
            act_floors = []
            for floor_nodes_data in act_floors_data:
                f_nodes = []
                for n_info in floor_nodes_data:
                    ntype_name = n_info.get("node_type", "MONSTER")
                    ntype = NodeType[ntype_name] if ntype_name in NodeType.__members__ else NodeType.MONSTER
                    node = MapNode(n_info["floor"], n_info["index"], ntype)
                    node.connections = list(n_info.get("connections", []))
                    node.visited = bool(n_info.get("visited", False))
                    node.available = bool(n_info.get("available", False))
                    f_nodes.append(node)
                act_floors.append(f_nodes)
            dungeon_map.act_maps[act_num] = act_floors

        if dungeon_map.act not in dungeon_map.act_maps:
            dungeon_map.act_maps[dungeon_map.act] = dungeon_map.floors

        curr_n_info = m_data.get("current_node")
        if curr_n_info and curr_n_info.get("floor") is not None and curr_n_info.get("index") is not None:
            cf = curr_n_info["floor"]
            ci = curr_n_info["index"]
            if cf < len(dungeon_map.floors) and ci < len(dungeon_map.floors[cf]):
                dungeon_map.current_node = dungeon_map.floors[cf][ci]
            else:
                dungeon_map.current_node = None
        else:
            dungeon_map.current_node = None

        return {
            "player": player,
            "dungeon_map": dungeon_map,
            "current_act": data.get("current_act", dungeon_map.act),
            "is_current_elite": data.get("is_current_elite", False),
            "is_current_boss": data.get("is_current_boss", False),
            "slot_id": slot_id
        }
    except Exception as e:
        print(f"[SaveManager] Error loading save slot {slot_id}: {e}")
        return None


def delete_save(slot_id: int) -> bool:
    """Deletes the save file for the specified slot."""
    save_path = get_save_path(slot_id)
    if os.path.exists(save_path):
        try:
            os.remove(save_path)
            return True
        except Exception as e:
            print(f"[SaveManager] Error deleting save slot {slot_id}: {e}")
            return False
    return False


def get_slot_info(slot_id: int) -> dict[str, Any]:
    """Returns metadata summary of a save slot for display in title/load screens."""
    save_path = get_save_path(slot_id)
    if not os.path.exists(save_path):
        return {"slot_id": slot_id, "exists": False}

    try:
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        p = data.get("player", {})
        m = data.get("dungeon_map", {})
        act = data.get("current_act", m.get("act", 1))
        curr_fl = m.get("current_floor", 0)
        cumul_fl = m.get("cumulative_floor", (act - 1) * 10 + curr_fl + 1)

        potions_count = sum(1 for pot in p.get("potions", []) if pot is not None)

        return {
            "slot_id": slot_id,
            "exists": True,
            "timestamp": data.get("timestamp", "Unknown date"),
            "saved_at_iso": data.get("saved_at_iso", ""),
            "char_id": p.get("char_id", "blood_knight"),
            "char_name": p.get("name", "Unknown Hero"),
            "class_title": p.get("class_title", ""),
            "hp": p.get("hp", 0),
            "max_hp": p.get("max_hp", 0),
            "gold": p.get("gold", 0),
            "act": act,
            "act_title": m.get("act_title", f"Act {act}"),
            "current_floor": curr_fl + 1,
            "cumulative_floor": cumul_fl,
            "deck_count": len(p.get("deck", [])),
            "relic_count": len(p.get("relics", [])),
            "potions_count": potions_count
        }
    except Exception as e:
        print(f"[SaveManager] Corrupt save in slot {slot_id}: {e}")
        return {"slot_id": slot_id, "exists": False, "corrupted": True}


def list_all_slots() -> list[dict[str, Any]]:
    """Returns summary for all NUM_SLOTS save slots."""
    return [get_slot_info(i) for i in range(1, NUM_SLOTS + 1)]


def has_any_save() -> bool:
    """Returns True if at least one valid save slot exists."""
    for i in range(1, NUM_SLOTS + 1):
        if get_slot_info(i).get("exists"):
            return True
    return False


def get_latest_save_slot() -> Optional[int]:
    """Returns the slot number of the most recently saved game, or None."""
    latest_slot = None
    latest_iso = ""
    for i in range(1, NUM_SLOTS + 1):
        info = get_slot_info(i)
        if info.get("exists"):
            iso = info.get("saved_at_iso", "")
            if latest_slot is None or iso > latest_iso:
                latest_iso = iso
                latest_slot = i
    return latest_slot


def get_first_empty_slot() -> int:
    """Returns the first empty slot number (1 to NUM_SLOTS), or 1 if all are occupied."""
    for i in range(1, NUM_SLOTS + 1):
        if not get_slot_info(i).get("exists"):
            return i
    return 1
