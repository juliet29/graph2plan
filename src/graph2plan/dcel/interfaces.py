import networkx as nx
from dataclasses import dataclass
from typing import Generic, NamedTuple, Literal
from typing import TypeVar

T = TypeVar("T")


@dataclass
class Coordinate:
    x: float
    y: float

    @property
    def pair(self):
        return (self.x, self.y)


@dataclass
class Edge(Generic[T]):
    u: T
    v: T
    ix: int
    pair_num: Literal[1, 2]
    # marked=False

    @property
    def name(self):
        return f"e{self.ix},{self.pair_num}"

    @property
    def pair(self):
        return (self.u, self.v)


@dataclass
class Edges(Generic[T]):
    edges: list[Edge[T]]

    def get(self, u: T, v: T):
        matches = [i for i in self.edges if i.u == u and i.v == v]
        assert len(matches) == 1
        return matches[0]


# TODO move to utils..


class Face(NamedTuple):
    ix: int


class Vertex(NamedTuple):
    ix: int


@dataclass
class VertexRecord:
    name: Vertex
    coordinate: Coordinate
    incident_edge: Edge


@dataclass
class FaceRecord:
    name: Face
    outer_component: Edge
    inner_compnent: Edge


@dataclass
class EdgeRecord:
    name: Edge
    origin: Vertex
    twin: Edge
    incident_face: Face
    next_edge: Edge
    prev_edge: Edge


VertexPositions = dict[int, tuple[int, int]]


def transform_graph_egdes(G: nx.Graph):
    ix = 0
    all_edges = []
    for e in G.edges:
        all_edges.append(Edge(e[0], e[1], ix, 1))
        ix += 1
        all_edges.append(Edge(e[1], e[0], ix, 2))
        ix += 1

    return Edges(all_edges)
