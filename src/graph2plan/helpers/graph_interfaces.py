from collections import namedtuple
from dataclasses import dataclass
from typing import Generic, Literal

from shapely import MultiPoint, centroid

from .geometry_interfaces import T, VertexPositions


@dataclass
class Face(Generic[T]):
    vertices: list[T]

    def __hash__(self) -> int:
        return hash(frozenset(self.vertices))

    def get_position(self, pos: VertexPositions):
        points = MultiPoint([pos[i] for i in self.vertices])
        x, y = centroid(points).xy
        return x[0], y[0]

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
