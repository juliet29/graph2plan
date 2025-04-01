from graph2plan.dcel.interfaces import Face
from graph2plan.dcel.interfaces import T

from typing import Generic, Literal, NamedTuple


class FacePair(Generic[T], NamedTuple):
    left: Face[T]
    right: Face[T]


EdgeFaceDict = dict[tuple[T, T], FacePair[T]]


class DualVertex(NamedTuple, Generic[T]):
    ix: int
    face: Face
    edge: tuple[T, T]
    side: Literal["LEFT", "RIGHT"]

    @property
    def name(self):
        return f"v_f{self.ix}"


class VertexDomain(NamedTuple):
    x_min: int
    x_max: int


MarkedNb = NamedTuple("MarkedNb", [("name", str), ("mark", Literal["IN", "OUT"])])
