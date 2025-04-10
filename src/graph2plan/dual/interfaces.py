from ast import Name
from dataclasses import dataclass
from graph2plan.helpers.general_interfaces import Face, ShapelyBounds
from graph2plan.helpers.general_interfaces import T
import matplotlib.pyplot as plt
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
    min: int
    max: int

    def check_is_valid(self):
        assert self.min < self.max, f"min {self.min} !< max {self.max}"

class Domain(NamedTuple):
    name: str
    bounds: ShapelyBounds

@dataclass
class Domains:
    domains: list[Domain]

    def get_domains_lim(self, PAD_BASE=1.4):
        PAD = PAD_BASE * 1.1
        min_x = min([i.bounds.min_x for i in self.domains]) - PAD
        max_x = max([i.bounds.max_x for i in self.domains]) + PAD
        min_y = min([i.bounds.min_y for i in self.domains]) - PAD
        max_y = max([i.bounds.max_y for i in self.domains]) + PAD
        return (min_x, max_x), (min_y, max_y)

    def draw(self):
        fig = plt.figure()
        ax = fig.add_subplot()
        xlim, ylim = self.get_domains_lim()
        for d in self.domains:
            patch = d.bounds.get_mpl_patch()
            ax.add_artist(patch)
            ax.annotate(d.name, (.5, .5), xycoords=patch, ha='center', va='bottom')
            # ax.text(d.bounds.mid_values.x, d.bounds.mid_values.y, d.name)
        
        # ax.autoscale_view()
        ax.set(xlim=xlim, ylim=ylim)


MarkedNb = NamedTuple("MarkedNb", [("name", str), ("mark", Literal["IN", "OUT"])])
