from dataclasses import dataclass
from graph2plan.helpers.general_interfaces import Face
from graph2plan.helpers.general_interfaces import T

from typing import Generic, Literal, NamedTuple


class FacePair(Generic[T], NamedTuple):
    left: Face[T]
    right: Face[T]


EdgeFaceDict = dict[tuple[T, T], FacePair[T]]


@dataclass
class DualVertex(Generic[T]):
    face: Face
    edge: tuple[T, T]
    side: Literal["LEFT", "RIGHT"]

    def name(self, ix):
        return f"v_f{ix}"


class VertexDomain(NamedTuple):
    x_min: int
    x_max: int


MarkedNb = NamedTuple("MarkedNb", [("name", str), ("mark", Literal["IN", "OUT"])])
