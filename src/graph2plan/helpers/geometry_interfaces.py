from collections import namedtuple
from dataclasses import dataclass
from typing import TypeVar

from matplotlib.patches import Rectangle
from shapely import Polygon

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
        # TODO use the centroid.. or create another that uses the centroid.. 
        x = (self.max_x - self.min_x) / 2 + self.min_x
        y = (self.max_y - self.min_y) / 2 + self.min_y
        return Mids(x, y)

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

    def get_mpl_patch(self):
        return Rectangle(
            (self.min_x, self.min_y),
            self.width,
            self.height,
            fill=False,
            edgecolor="black",
            alpha=0.2,
        )

    def get_rectangular_coords(self):
        """counterclocksie starting at bottom left"""
        coords = [
            Coordinate(self.min_x, self.min_y),
            Coordinate(self.max_x, self.min_y),
            Coordinate(self.max_x, self.max_y),
            Coordinate(self.min_x, self.max_y),
        ]
        return coords

    def to_shapely_rectangle(self):
        coords = self.get_rectangular_coords()
        polygon = Polygon([i.pair for i in coords])
        return polygon


@dataclass
class CoordinateList:
    coordinates: list[Coordinate]

    @property
    def bounds(self):
        xs = [i.x for i in self.coordinates]
        ys = [i.y for i in self.coordinates]
        return ShapelyBounds(min(xs), min(ys), max(xs), max(ys))
    
    def extreme_coord(self):
        min_x = min([i.x for i in self.coordinates])
        potential_points = [i for i in self.coordinates if i.x == min_x]
        return sorted(potential_points, key=lambda i: i.y)[0]


    @classmethod
    def to_coordinate_list(cls, pos: VertexPositions):
        return cls([Coordinate(*i) for i in pos.values()])
    
    @classmethod
    def name_extreme_coord(cls, pos: VertexPositions):
        c = cls.to_coordinate_list(pos)
        extrema = [k for k,v in pos.items() if v == c.extreme_coord().pair]
        assert len(extrema) == 1
        return extrema[0]

