"""
Procedural Node Map Generator for Slay the Spire-style dungeon progression.
"""
from enum import Enum
import random

class NodeType(Enum):
    MONSTER = "Monster"
    ELITE = "Elite"
    EVENT = "Event"
    REST = "Rest"
    SHOP = "Shop"
    BOSS = "Boss"

class MapNode:
    def __init__(self, floor: int, index: int, node_type: NodeType):
        self.floor = floor
        self.index = index
        self.node_type = node_type
        self.connections: list[int] = []  # indices of connected nodes in floor + 1
        self.visited = False
        self.available = False

class DungeonMap:
    def __init__(self, num_floors: int = 10, paths_per_floor: int = 3, act: int = 1, seed: int = None):
        self.num_floors = num_floors
        self.paths_per_floor = paths_per_floor
        self.act = act
        self.seed = seed if seed is not None else random.randint(1, 99999999)
        self.floors: list[list[MapNode]] = []
        self.current_floor = 0
        self.current_node: MapNode = None
        self.act_maps: dict[int, list[list[MapNode]]] = {}
        self.generate()

    def get_act_title(self, act_num: int = None) -> str:
        act = self.act if act_num is None else act_num
        if act == 1:
            return "ACT I - CRYPT OF THE NECROLORD"
        elif act == 2:
            return "ACT II - THE MOLTEN BASTION"
        elif act == 3:
            return "ACT III - THE ABYSSAL CITADEL"
        return f"ACT {act} - ETERNAL SPIRE (ASCENSION {act - 3})"

    def get_cumulative_floor(self) -> int:
        return (self.act - 1) * self.num_floors + self.current_floor + 1

    def get_act_floors(self, act_num: int) -> list[list[MapNode]]:
        """Returns the floor layout for any Act, generating deterministically on demand."""
        if act_num == self.act and self.floors:
            return self.floors
        if not hasattr(self, 'act_maps'):
            self.act_maps = {}
        if act_num not in self.act_maps:
            self.act_maps[act_num] = self._generate_floors_for_act(act_num)
        return self.act_maps[act_num]

    def _generate_floors_for_act(self, act_num: int) -> list[list[MapNode]]:
        """Generates a complete 10-floor branching dungeon map for the given Act."""
        rng = random.Random(self.seed + act_num * 1000)
        floors = []

        for f in range(self.num_floors):
            floor_nodes = []
            
            if f == self.num_floors - 1:
                # Final floor is Boss
                node = MapNode(f, 0, NodeType.BOSS)
                floor_nodes.append(node)
            elif f == 0:
                # First floor: monster encounters
                for i in range(self.paths_per_floor):
                    node = MapNode(f, i, NodeType.MONSTER)
                    floor_nodes.append(node)
            elif f == self.num_floors - 2:
                # Pre-boss floor: Rest site
                for i in range(self.paths_per_floor):
                    node = MapNode(f, i, NodeType.REST)
                    floor_nodes.append(node)
            elif f == 5:
                # Mid-dungeon Rest or Shop
                for i in range(self.paths_per_floor):
                    ntype = NodeType.REST if i % 2 == 0 else NodeType.SHOP
                    floor_nodes.append(MapNode(f, i, ntype))
            else:
                # Intermediate floors
                types_pool = [NodeType.MONSTER, NodeType.MONSTER, NodeType.EVENT, NodeType.EVENT]
                if f >= 4:
                    types_pool.append(NodeType.ELITE)
                if f >= 3:
                    types_pool.append(NodeType.SHOP)

                for i in range(self.paths_per_floor):
                    ntype = rng.choice(types_pool)
                    floor_nodes.append(MapNode(f, i, ntype))

            floors.append(floor_nodes)

        # Generate connections between adjacent floors
        for f in range(self.num_floors - 1):
            curr_nodes = floors[f]
            next_nodes = floors[f + 1]

            if len(next_nodes) == 1:
                # Boss floor connects from all
                for node in curr_nodes:
                    node.connections = [0]
            else:
                for i, node in enumerate(curr_nodes):
                    conns = {i}
                    if i > 0 and rng.random() < 0.4:
                        conns.add(i - 1)
                    if i < len(next_nodes) - 1 and rng.random() < 0.4:
                        conns.add(i + 1)
                    node.connections = sorted(list(conns))

        return floors

    def generate(self):
        if not hasattr(self, 'seed') or self.seed is None:
            self.seed = random.randint(1, 99999999)
        if not hasattr(self, 'act_maps'):
            self.act_maps = {}

        self.floors = self._generate_floors_for_act(self.act)
        self.act_maps[self.act] = self.floors
        self.current_floor = 0
        self.current_node = None

        # Initially, all floor 0 nodes in current act are available
        for node in self.floors[0]:
            node.available = True

    def advance_to_act(self, next_act: int):
        """Advances the map to the next Act, preserving past act records."""
        if not hasattr(self, 'act_maps'):
            self.act_maps = {}
        self.act_maps[self.act] = self.floors

        self.act = next_act
        self.floors = self.get_act_floors(next_act)
        self.current_floor = 0
        self.current_node = None
        for node in self.floors[0]:
            node.available = True

    def select_node(self, node: MapNode) -> bool:
        if not node.available:
            return False
        
        self.current_node = node
        self.current_floor = node.floor
        node.visited = True

        # Update available nodes for next floor
        for f_nodes in self.floors:
            for n in f_nodes:
                n.available = False

        if node.floor + 1 < self.num_floors:
            next_nodes = self.floors[node.floor + 1]
            for target_idx in node.connections:
                if target_idx < len(next_nodes):
                    next_nodes[target_idx].available = True

        return True
