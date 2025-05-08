## TODO not really 4TP, more so prep for dual..


from copy import deepcopy
from dataclasses import dataclass
from pprint import pprint

from graph2plan.dual.helpers import get_embedding_faces
from graph2plan.fourtp.draw_four_complete import draw_four_complete_graph
from graph2plan.fourtp.faces import get_embedding_of_four_complete_G, get_external_face
from graph2plan.helpers.geometry_interfaces import VertexPositions
from graph2plan.helpers.utils import set_difference

import networkx as nx


@dataclass
class VertexData:
    name: str
    ordered_number = -1
    is_marked = False
    n_marked_nbs = 0  # visited
    n_chords = 0

    def __repr__(self) -> str:
        return f"{self.name, self.ordered_number} | is_marked: {self.is_marked}, n_marked_nbs: {self.n_marked_nbs}, n_chords: {self.n_chords} "

    @property
    def is_potential_next(self):
        if not self.is_marked and self.n_marked_nbs >= 2 and self.n_chords == 0:
            # print(f"{self.name} is potential next")
            return True
        return False


@dataclass
class CanonicalOrder:
    vertices: dict[str, VertexData]
    u: str
    v: str
    w: str  # => v_n
    n: int  # number of vertices
    k: int = 3

    @property
    def unmarked(self):
        return [i.name for i in self.vertices.values() if not i.is_marked]
    
    @property
    def unordered(self):
        return [i.name for i in self.vertices.values() if i.ordered_number < 0]

    @property
    def Gk_nodes(self):
        return [
            i.name
            for i in self.vertices.values()
            if i.ordered_number > 0 and i.ordered_number <= self.k
        ]

    @property
    def Gk_minus_1_nodes(self):
        return [
            i.name
            for i in self.vertices.values()
            if i.ordered_number > 0 and i.ordered_number < self.k
        ]

    @property
    def G_diff_Gk_minus_1_nodes(self):
        return [
            i.name
            for i in self.vertices.values()
            if i.name not in self.Gk_minus_1_nodes
        ]

    def increment_k(self):
        print(f"incrementing k from {self.k} to {self.k + 1}")
        self.k += 1

    def potential_vertices(self):
        return [
            i
            for i in self.vertices.values()
            if i.is_potential_next
            and i.name != self.u
            and i.name != self.v
            and i.name != self.w
        ]  # TODO prevent from selecting v_n..

    def show_vertices(self):
        s = sorted(
            list(self.vertices.values()),
            key=lambda x: (x.ordered_number, x.n_marked_nbs),
            reverse=True,
        )
        pprint(s)


@dataclass
class G_canonical:
    G: nx.Graph  # should be undirected..
    pos: VertexPositions  # should be put to be one..
    full_pos: VertexPositions

    @property
    def embedding(self):
        return get_embedding_of_four_complete_G(self.G, self.full_pos)

    def get_outer_face_of_nodes(self, nodes_to_keep: list, print_other_faces=False):
        nodes_to_remove = set_difference(self.embedding.nodes, nodes_to_keep)

        _embedding = deepcopy(self.embedding)
        _embedding.remove_nodes_from(nodes_to_remove)
        if print_other_faces:
            other_faces = get_embedding_faces(_embedding)
            print(f"==>> other_faces: {other_faces}")

        return get_external_face(_embedding, self.full_pos)

    def outer_face_at_k(self, co: CanonicalOrder):
        return self.get_outer_face_of_nodes(co.Gk_nodes)

    def outer_face_at_k_minus_1(self, co: CanonicalOrder):
        return self.get_outer_face_of_nodes(co.Gk_minus_1_nodes)

    def outer_face_of_unmarked(self, co: CanonicalOrder):
        return self.get_outer_face_of_nodes(co.unmarked, print_other_faces=False)

    def draw(self, nodes_to_include: list):
        G_to_draw = self.G.subgraph(nodes_to_include)
        draw_four_complete_graph(G_to_draw, self.pos, self.full_pos)


class NotImplementedError(Exception):
    pass


class CanonicalOrderingFailure(Exception):
    pass

class EmbeddingFailure(Exception):
    pass
