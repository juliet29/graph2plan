from copy import deepcopy
from dataclasses import dataclass
from typing import Union
import networkx as nx
from pprint import pprint

from networkx import is_chordal

from graph2plan.helpers.geometry_interfaces import VertexPositions
from .draw_four_complete import draw_four_complete_graph
from ..dcel.original import create_embedding

## TODO not really 4TP, more so prep for dual..


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
            print(f"{self.name} is potential next")
            return True
        return False


@dataclass
class CanonicalOrder:
    vertices: dict[str, VertexData]
    u: str
    v: str
    w: str  # => v_n
    x: str  # "current node.." => v_w
    # n: int
    n: int  # number of vertices
    k: int

    # @property
    # def num_vertices(self):
    #     return len(self.vertices)

    # @property
    # def curr_k(self):
    #     return self.k

    def decrement_k(self):
        self.k -= 1
        print(f"decrementing k from {self.k + 1} to {self.k}")

    @property
    def unmarked(self):
        return [i.name for i in self.vertices.values() if not i.is_marked]

    @property
    def Gk_minus_1(self):
        return [
            i.name
            for i in self.vertices.values()
            if i.ordered_number > 0 and i.ordered_number < self.k
        ]

    @property
    def Gk(self):
        return [
            i.name
            for i in self.vertices.values()
            if i.ordered_number > 0 and i.ordered_number <= self.k
        ]

    def potential_vertices(self):
        return [
            i
            for i in self.vertices.values()
            if i.is_potential_next and i.name != self.u and i.name != self.v
        ]

    def show_vertices(self):
        s = sorted(
            list(self.vertices.values()),
            key=lambda x: (x.ordered_number, x.n_marked_nbs),
            reverse=True,
        )
        pprint(s)
@dataclass
class G_canonical:
    G: nx.Graph
    pos: VertexPositions
    full_pos: VertexPositions

    @property
    def embedding(self):
        return create_embedding(self.G, self.full_pos) # TODO this could be wrong.. 

    def outer_face(self):
        pass



def update_neighbors_visited(G: nx.Graph, co: CanonicalOrder, vertex_name):
    nbs = G.neighbors(vertex_name)

    nbs_to_update = [i for i in nbs if not co.vertices[i].is_marked]
    print(f"updating nbs of vertex {vertex_name}: {nbs_to_update}")
    for nb in nbs_to_update:
        co.vertices[nb].n_marked_nbs += 1


def update_chords(
    G: nx.Graph, co: CanonicalOrder, pos: VertexPositions, full_pos: VertexPositions
):
    G_unmarked = G.subgraph(co.unmarked)
    if nx.is_chordal(G_unmarked):
        draw_four_complete_graph(G_unmarked, pos, full_pos)
        raise Exception("Haven't handled chordal graph! ")
        # TODO -> update the co.chords variable for each node and all its nbs
    # otherwise do nothing..


def initialize_canonical_order(_G: nx.Graph, pos, full_pos):
    # TODO -> test that graph is 4TP
    G = deepcopy(_G).to_undirected()
    vertices = {i: VertexData(i) for i in G.nodes}
    co = CanonicalOrder(
        vertices, u="v_s", v="v_e", w="v_n", x="v_w", k=G.order(), n=G.order()
    )

    # mark and order the starting nodes, but dont update their nbs
    co.vertices[co.u].is_marked = True
    co.vertices[co.v].is_marked = True
    co.vertices[co.u].ordered_number = 1
    co.vertices[co.v].ordered_number = 2

    # set v_n(orth), and v_w to be v_n and v_n-1, and update their nbs
    # TODO check v_n(orth) is valid, check 1 only

    co.vertices[co.w].n_marked_nbs = 2
    co.vertices[co.w].is_marked = True
    co.vertices[co.w].ordered_number = co.k
    update_neighbors_visited(G, co, co.w)
    update_chords(G, co, pos, full_pos)
    co.decrement_k()

    # no vertices will yet have up to two neighbors, so pick v_w
    # TODO check (v_w is valid, check 1 and 2.1)
    co.vertices[co.x].is_marked = True
    co.vertices[co.w].ordered_number = co.k
    update_neighbors_visited(G, co, co.x)
    update_chords(G, co, pos, full_pos)
    co.decrement_k()

    # now should have 1 potential nb
    assert len(co.potential_vertices()) == 1

    return G, co


def iterate_canonical_order(G: nx.Graph, co: CanonicalOrder, pos, full_pos):
    while co.k > 4:
        potential = co.potential_vertices()
        if len(potential) == 0:
            print(f"No potential vertices: {co.show_vertices()}")
            raise Exception
        if len(potential) > 1:
            print(
                f"Multiple potential: {[i.name for i in potential]}. Would choose {potential[0].name}.  {co.show_vertices()}"
            )
            raise Exception

        vk = potential[0]
        # TODO assert vk is valid
        co.vertices[vk.name].is_marked = True
        co.vertices[vk.name].ordered_number = co.k
        update_neighbors_visited(G, co, vk.name)
        update_chords(G, co, pos, full_pos)
        co.decrement_k()

    return G, co

    # co.vertices[vk.name].ordered_number = k
    # co.vertices[vk.name].is_marked = True

    # # update the visited of its neighbors..
    # update_neighbors_visited(G, co, vk.name)
    # update_neighbors_visited(G, co, co.u)
    # update_neighbors_visited(G, co, co.v)

    # print(f"k={k}, vk={vk.name}")
    # # co.show_vertices()

    # co.decrement_k()

    return G, co

