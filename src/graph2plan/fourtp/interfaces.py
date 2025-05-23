from enum import Enum
from typing import NamedTuple

from graph2plan.helpers.graph_interfaces import CardinalDirectionEnum as CDE


class Alphas(Enum):
    NE = 0
    SE = 1
    SW = 2
    NW = 3


alpha_mapping: dict[CDE, tuple[Alphas, Alphas]] = {
    # counter clockwise orientation here
    CDE.NORTH: (Alphas.NW, Alphas.NE),
    CDE.EAST: (Alphas.NE, Alphas.SE),
    CDE.SOUTH: (Alphas.SE, Alphas.SW),
    CDE.WEST: (Alphas.SW, Alphas.NW),
}


class CardinalPath(NamedTuple):
    drn: CDE
    path: list

    def __repr__(self) -> str:
        return f"{(self.drn.name, self.path)}"
