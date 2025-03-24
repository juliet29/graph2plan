from dataclasses import dataclass
from typing import NamedTuple, Literal




@dataclass
class Coordinate:
    x: float
    y: float

@dataclass
class Edge:
    u: int
    v: int
    number: int
    pair_num: Literal[1,2]

    def name(self):
        return f"e{self.number},{self.pair_num}"


class Face(NamedTuple):
    number: int


class Vertex(NamedTuple):
    number: int




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
