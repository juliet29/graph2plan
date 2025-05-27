import functools
from copy import deepcopy

import networkx as nx
from matplotlib import pyplot as plt

from .canonical_helpers import (
    check_and_update_chords,
    update_neighbors_visited,
)
from .canonical_interfaces import (
    CanonicalOrder,
    G_canonical,
    VertexData,
)
from graph2plan.dcel.interfaces import CanonicalOrderingFailure
from graph2plan.helpers.geometry_interfaces import VertexPositions

from .check_canonical import vk_permits_valid_order


def initialize_canonical_order(_G: nx.Graph, pos, full_pos):
    # TODO -> test that graph is 4TP
    G = deepcopy(_G).to_undirected()
    
    G_c = G_canonical(G, pos, full_pos)
    vertices = {i: VertexData(i) for i in G.nodes}
    co = CanonicalOrder(vertices, u="v_s", v="v_w", w="v_n", n=G.order())

    # mark and order the starting nodes, but dont update their nbs
    for ix, node in enumerate([co.u, co.v]):
        co.vertices[node].ordered_number = ix + 1
        co.vertices[node].is_marked = True
        update_neighbors_visited(G, co, node)

    co.vertices[co.w].ordered_number = co.n
    co.vertices[co.w].n_marked_nbs = 2

    assert len(co.potential_vertices()) == 1

    return G_c, co


@functools.lru_cache
def iterate_canonical_order(G_c: G_canonical, co: CanonicalOrder):
    count = 0
    print(co.k, co.n)
    while co.k < co.n - 1:
        potential = co.potential_vertices()
        if len(potential) == 0:
            raise Exception("No potential vertices!")

        if len(potential) > 1:
            print(
                f"Multiple potential: {[i.name for i in potential]}. Choosing {potential[0].name}"
            )

        vk = potential[0]
        try:
            co.vertices[vk.name].ordered_number = co.k
            vk_permits_valid_order(G_c, co, vk.name)
        except CanonicalOrderingFailure:
            G_c.draw(co.unmarked)
            co.show_vertices()
            raise Exception(
                f"While iterating, ordering {vk.name} failed.. time to try breadth-first search?"
            )

        co.vertices[vk.name].is_marked = True

        update_neighbors_visited(G_c.G, co, vk.name)
        check_and_update_chords(G_c, co, vk.name)
        co.increment_k()

        count += 1

        if count > co.n:
            raise Exception("Iterations have exceeded number of nodes.. breaking!")

    print("Time to order the last node..")
    assert len(co.unordered) == 1, f"More than 1 unordered node! {co.unordered}"
    vk = co.unordered[0]
    co.vertices[vk].ordered_number = co.k

    return G_c, co


def create_canonical_order(G, pos, full_pos):
    G_c, co = initialize_canonical_order(G, pos, full_pos)
    print("-----Initialization complete---")
    G_c, co = iterate_canonical_order(G_c, co)
    print("-----Canonical ordering complete---")
    return G_c, co 

