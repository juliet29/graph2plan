## TODO not really 4TP, more so prep for dual..


import json
from copy import deepcopy
from dataclasses import dataclass
from pprint import pprint

import matplotlib.pyplot as plt
import networkx as nx

from graph2plan.dual.helpers import get_embedding_faces
from graph2plan.fourtp.draw_four_complete import (
    compute_and_draw_edges,
    draw_four_complete_graph,
)
from graph2plan.fourtp.faces import get_embedding_of_four_complete_G, get_external_face
from graph2plan.helpers.geometry_interfaces import VertexPositions
from graph2plan.helpers.utils import set_difference

from ..constants import BASE_PATH


class CanonicalOrderingFailure(Exception):
    pass


CanonicalVertices = dict[str, int]


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

    def __hash__(self) -> int:
        return hash(frozenset(self.co_vertices))
        # return hash(
        #     frozenset((i.name, i.ordered_number) for i in self.vertices.values())
        # )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CanonicalOrder):
            return self.co_vertices == other.co_vertices
        raise NotImplementedError("Can't compare a non-canon order!")


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

    # @property # TODO this could cause an error 5/12/25..
    def Gk_minus_1_nodes(self, k=None):
        if not k:
            k = self.k
        return [
            i.name
            for i in self.vertices.values()
            if i.ordered_number > 0 and i.ordered_number < k
        ]

    @property
    def G_diff_Gk_minus_1_nodes(self):
        return [
            i.name
            for i in self.vertices.values()
            if i.name not in self.Gk_minus_1_nodes()
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

    @property
    def co_vertices(self) -> CanonicalVertices:
        return {k: v.ordered_number for k, v in self.vertices.items()}


@dataclass
class G_canonical:
    G: nx.Graph  # should be undirected..
    pos: VertexPositions  # should be put to be one..
    full_pos: VertexPositions

    def __hash__(self) -> int:
        return hash(nx.weisfeiler_lehman_graph_hash(self.G))
    

    def __eq__(self, other: object) -> bool:
        if isinstance(other, G_canonical):
            return nx.utils.graphs_equal(self.G, other.G)
        raise NotImplementedError("Can't compare a non G_canonical!")

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

    def outer_face_at_k_minus_1(self, co: CanonicalOrder, k=None):
        return self.get_outer_face_of_nodes(co.Gk_minus_1_nodes(k))

    def outer_face_of_unmarked(self, co: CanonicalOrder):
        return self.get_outer_face_of_nodes(co.unmarked, print_other_faces=False)

    def draw(self, nodes_to_include: list):
        G_to_draw = self.G.subgraph(nodes_to_include)
        draw_four_complete_graph(G_to_draw, self.pos, self.full_pos)

    def draw_co(self, co: CanonicalOrder):
        fig, ax = plt.subplots(1, 1)
        compute_and_draw_edges(self.G, self.pos, self.full_pos, ax)
        nx.draw_networkx_nodes(
            self.G, self.full_pos, ax=ax, node_size=400, node_shape="s"
        )
        nx.draw_networkx_labels(
            self.G,
            self.full_pos,
            ax=ax,
            labels={n: f"{co.vertices[n].ordered_number}\n({n})" for n in self.G.nodes},
            font_size=8,
        )
        # nx.draw_networkx_edges(self.G, self.full_pos, ax=ax)
        plt.show()


def write_canonical_outputs(G_c: G_canonical, co: CanonicalOrder):
    path = BASE_PATH / "canonical_outputs"
    # TODO add intermediate folder -> kk85..
    G_json = nx.node_link_data(G_c.G, edges="edges")
    with open(path / "graph.json", "w+") as file:
        json.dump(G_json, default=str, fp=file)

    # TODO add to class
    co_vertices = {k: v.ordered_number for k, v in co.vertices.items()}
    with open(path / "co_vertices.json", "w+") as file:
        json.dump(co_vertices, default=str, fp=file)

    # vertex positions..
    with open(path / "pos.json", "w+") as file:
        json.dump(G_c.full_pos, default=str, fp=file)


def read_canonical_outputs():
    path = BASE_PATH / "canonical_outputs"
    with open(path / "graph.json", "r") as file:
        d = json.load(file)
    G: nx.Graph = nx.node_link_graph(d, edges="edges")

    with open(path / "co_vertices.json", "r") as file:
        co_vertices: CanonicalVertices = json.load(file)

    with open(path / "pos.json", "r") as file:
        p = json.load(file)

    pos: VertexPositions = {k: tuple(v) for k, v in p.items()}

    return G, co_vertices, pos
