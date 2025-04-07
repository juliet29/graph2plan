from collections import namedtuple
from dataclasses import dataclass

from shapely import MultiPoint, centroid
from typing import Generic, Literal, TypeVar

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
            return True if (value.x == self.x) and (value.y == self.y) else False
        raise Exception("Invalid object for comparison")


Mids = namedtuple("Mids", ["x", "y"])
CardinalPos = namedtuple("CardinalPos", ["v_n", "v_e", "v_s", "v_w"])


@dataclass
class ShapelyBounds:
    """[based on Shapely bounds attribute](https://shapely.readthedocs.io/en/stable/reference/shapely.MultiPoint.html#shapely.MultiPoint.bounds)"""

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y

    @property
    def mid_values(self):
        # TODO use the centroid..
        mid_x = (self.max_x - self.min_x) / 2 + self.min_x
        mid_y = (self.max_y - self.min_y) / 2 + self.min_y
        return Mids(mid_x, mid_y)

    def cardinal_values(self):
        return CardinalPos(
            (self.mid_values.x, self.max_y),
            (self.max_x, self.mid_values.y),
            (self.mid_values.x, self.min_y),
            (self.min_x, self.mid_values.y),
        )

    def circular_cardinal_values(self):
        r = max(self.width / 2, self.height / 2) * (1.01)
        left_x = self.mid_values.x - r
        right_x = self.mid_values.x + r
        bottom_y = self.mid_values.y - r
        top_y = self.mid_values.y + r

        return CardinalPos(
            (self.mid_values.x, top_y),
            (right_x, self.mid_values.y),
            (self.mid_values.x, bottom_y),
            (left_x, self.mid_values.y),
        )


@dataclass
class CoordinateList:
    coordinates: list[Coordinate]

    @property
    def bounds(self):
        xs = [i.x for i in self.coordinates]
        ys = [i.y for i in self.coordinates]
        return ShapelyBounds(min(xs), max(xs), min(ys), max(ys))

    @classmethod
    def to_coordinate_list(cls, pos: VertexPositions):
        return cls([Coordinate(*i) for i in pos.values()])

    @property
    def mid_values(self):
        bounds = self.bounds
        mid_x = (bounds.max_x - bounds.min_x) / 2 + bounds.min_x
        mid_y = (bounds.max_y - bounds.min_y) / 2 + bounds.min_y
        Mids = namedtuple("Mids", ["x", "y"])
        return Mids(mid_x, mid_y)


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
        # TODO similarity up to cycled order..
        raise Exception("Invalid object for comparison")

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
