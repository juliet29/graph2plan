import networkx as nx
from dataclasses import dataclass
from typing import Generic, NamedTuple, Literal
from typing import TypeVar
from collections import deque

from graph2plan.helpers.general_interfaces import Coordinate
from graph2plan.helpers.general_interfaces import Face
from graph2plan.helpers.general_interfaces import T


@dataclass
class Edge(Generic[T]):
    u: T
    v: T
    ix: int = 0
    pair_num: Literal[1, 2] = 1
    # marked=False

    @property
    def name(self):
        return f"e{self.ix},{self.pair_num}"

    @property
    def pair(self):
        return (self.u, self.v)

    def __hash__(self) -> int:
        return hash(frozenset(self.pair))

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Edge):
            return True if frozenset(value.pair) == frozenset(self.pair) else False
        raise Exception("Invalid object for comparison")


@dataclass
class Edges(Generic[T]):
    edges: list[Edge[T]]

    def get(self, u: T, v: T):
        matches = [i for i in self.edges if i.u == u and i.v == v]
        assert len(matches) == 1
        return matches[0]

    def find_unique(self):
        s = set(self.edges)
        assert len(s) == 0.5 * (len(self.edges))
        return s


# TODO move to utils..


class Vertex(NamedTuple):
    ix: int


def transform_graph_egdes(G: nx.Graph):
    ix = 0
    all_edges = []
    for e in G.edges:
        all_edges.append(Edge(e[0], e[1], ix, 1))
        ix += 1
        all_edges.append(Edge(e[1], e[0], ix, 2))
        ix += 1

    return Edges(all_edges)


def compare_order_of_faces(f1: Face, f2: Face):
    # v1  = deque(ef['v_s','v_w'].left_face.vertices)
    # v2 = deque(ef['v_s','v_e'].right_face.vertices)

    v1 = deque(f1.vertices)
    v2 = deque(f1.vertices)

    ix = v1.index("v_w")
    ix2 = v2.index("v_w")
    diff = ix2 - ix
    print(diff)
    v2.rotate(diff - 1)
