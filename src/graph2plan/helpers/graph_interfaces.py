from collections import namedtuple
from dataclasses import dataclass
from typing import Generic, Literal, NamedTuple
from enum import Enum

from shapely import MultiPoint, centroid, Polygon
from shewchuk import orientation

from graph2plan.dcel.original import create_line

from .geometry_interfaces import T, VertexPositions

from sympy import Triangle, Point
from graph2plan.dcel.interfaces import Edge
import networkx as nx
from numpy import sign


@dataclass
class Face(Generic[T]):
    vertices: list[T]

    def __hash__(self) -> int:
        return hash(frozenset(self.vertices))

    def points(self, pos: VertexPositions):
        return [pos[i] for i in self.vertices]

    def get_position(self, pos: VertexPositions):
        x, y = centroid(MultiPoint(self.points(pos))).xy
        return x[0], y[0]

    def get_signed_area(self, pos: VertexPositions):
        assert len(self.vertices) == 3, f"Face  {self.vertices} ! have 3 vertices. Not appropriate to calculate signed area with this method."
        Gcycle = nx.cycle_graph(self.vertices, nx.DiGraph)
        edges = [Edge(*e) for e in Gcycle.edges]
        # print([(e.u, e.v) for e in edges])

        l1, l2 = [create_line(e, pos) for e in edges[:2]]
        assert l1 and l2
        triangle = Triangle(*l1.points, l2.points[1])
        # points = self.points(pos)
        # # print(points)
        # triangle = Triangle(*[Point(i) for i in points])
        assert isinstance(triangle, Triangle), "These points do not make a triangle!"
        return sign(triangle.area)

        # try:
        #     p = Polygon(self.points(pos))
        #     return p.area
        # except ValueError:
        #     raise Exception(f"Problem getting area of face {self.vertices}!")

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Face):
            return (
                True if frozenset(value.vertices) == frozenset(self.vertices) else False
            )
        # TODO similarity up to cycled order, but hasnt been needed so far..
        raise Exception("Invalid object for comparison")

    @property
    def n_vertices(self):
        return len(self.vertices)


Axis = Literal["x", "y"]
Assignments = namedtuple(
    "Assignments", ["source", "target", "other_source", "other_target"]
)
assignments = {
    "x": Assignments("v_w", "v_e", "v_s", "v_n"),
    "y": Assignments(
        "v_s",
        "v_n",
        "v_w",
        "v_e",
    ),
}


# TODO use this everywhere
def get_assignments(axis: Axis):
    return assignments[axis]


node_aliases = {
    "v_n": "n*",
    "v_s": "s*",
    "v_e": "e*",
    "v_w": "w*",
}


def get_node_alias(node: str):
    return node_aliases[node]


# class AxisEnum(Enum):
#     X = 0
#     Y = 1

# class OrientationEnum(Enum):
#     IN = 0
#     OUT = 1

OrientationOptions = Literal["IN", "OUT"]
CardinalOptions = Literal["NORTH", "EAST", "SOUTH", "WEST"]


class CardinalDirectionEnum(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class CardinalDirectionData(NamedTuple):
    enum: CardinalDirectionEnum
    orientation: OrientationOptions
    axis: Axis

    @property
    def vertex_name(self):
        return f"v_{self.enum.name[0].lower()}"


# # TODO could be a dict?
# cardinal_directions = [
#     CardinalDirection("NORTH", "IN", "y"),
#     CardinalDirection("SOUTH", "OUT", "y"),
#     CardinalDirection("EAST", "IN", "x"),
#     CardinalDirection("WEST", "OUT", "x")
# ]

cardinal_directions: dict[CardinalDirectionEnum, CardinalDirectionData] = {
    CardinalDirectionEnum.NORTH: CardinalDirectionData(
        CardinalDirectionEnum.NORTH, "IN", "y"
    ),
    CardinalDirectionEnum.EAST: CardinalDirectionData(
        CardinalDirectionEnum.EAST, "IN", "x"
    ),
    CardinalDirectionEnum.SOUTH: CardinalDirectionData(
        CardinalDirectionEnum.SOUTH, "OUT", "y"
    ),
    CardinalDirectionEnum.WEST: CardinalDirectionData(
        CardinalDirectionEnum.WEST, "OUT", "x"
    ),
}


def get_vertex_name(drn: CardinalDirectionEnum):
    return cardinal_directions[drn].vertex_name
