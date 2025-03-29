import networkx as nx
from dataclasses import dataclass
from typing import Generic, NamedTuple, Literal
from typing import TypeVar, Sequence
from collections import namedtuple
from collections import deque
from shapely import centroid, MultiPoint

T = TypeVar("T")
VertexPositions = dict[T, tuple[float, float]]



@dataclass
class Coordinate:
    x: float
    y: float

    @property
    def pair(self):
        return (self.x, self.y)
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Coordinate):
            return True if (value.x == self.x) and (value.y == self.y) else  False
        raise Exception("Invalid object for comparison")

Bounds = namedtuple("Bounds", ["min_x", "max_x","min_y","max_y",])

@dataclass
class CoordinateList:
    coordinates: list[Coordinate]

    @property
    def bounds(self):
        xs = [i.x for i in self.coordinates]
        ys = [i.y for i in self.coordinates]
        return Bounds(min(xs), max(xs), min(ys), max(ys))
    
    @classmethod
    def to_coordinate_list(cls, pos:VertexPositions):
        return cls([Coordinate(*i) for i in pos.values()])
    
    @property
    def mid_values(self):
        bounds = self.bounds
        mid_x = (bounds.max_x - bounds.min_x)/2 + bounds.min_x
        mid_y = (bounds.max_y - bounds.min_y)/2 + bounds.min_y
        Mids = namedtuple("Mids", ["x", "y"])
        return Mids(mid_x, mid_y)
    


@dataclass
class Edge(Generic[T]):
    u: T
    v: T
    ix: int = 0
    pair_num: Literal[1, 2] =1
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
        assert len(s) == 0.5*(len(self.edges))
        return s


# TODO move to utils..

@dataclass
class Face(Generic[T]):
    vertices: list[T]

    # def __hash__(self) -> int:
    #     return super().__hash__()

    def get_position(self, pos: VertexPositions):
        points = MultiPoint([pos[i] for i in self.vertices])
        x,y = centroid(points).xy
        return x[0],y[0]

    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Face):
            return True if set(value.vertices) == set(self.vertices) else  False
        # TODO similarity up to cycled order.. 
        raise Exception("Invalid object for comparison")


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





def transform_graph_egdes(G: nx.Graph):
    ix = 0
    all_edges = []
    for e in G.edges:
        all_edges.append(Edge(e[0], e[1], ix, 1))
        ix += 1
        all_edges.append(Edge(e[1], e[0], ix, 2))
        ix += 1

    return Edges(all_edges)


def compare_order_of_faces(f1:Face, f2:Face):
    # v1  = deque(ef['v_s','v_w'].left_face.vertices)
    # v2 = deque(ef['v_s','v_e'].right_face.vertices)

    v1 = deque(f1.vertices)
    v2 = deque(f1.vertices)
    
    ix = v1.index("v_w")
    ix2 = v2.index("v_w")
    diff = ix2 - ix
    print(diff)
    v2.rotate(diff-1)
    