from copy import deepcopy
from typing import Union
import networkx as nx
from .check_canonical import is_Gk_minus_1_biconnected, are_u_v_in_Ck


from graph2plan.fourtp.canonical_interfaces import (
    CanonicalOrder,
    G_canonical,
    VertexData,
)
from .draw_four_complete import draw_four_complete_graph
from ..dcel.original import create_embedding


def update_neighbors_visited(G: nx.Graph, co: CanonicalOrder, vertex_name):
    nbs = G.neighbors(vertex_name)

    nbs_to_update = [i for i in nbs if not co.vertices[i].is_marked]
    print(f"updating nbs of vertex {vertex_name}: {nbs_to_update}")
    for nb in nbs_to_update:
        co.vertices[nb].n_marked_nbs += 1


def update_chords(G_c: G_canonical, co: CanonicalOrder):
    G_unmarked = G_c.G.subgraph(co.unmarked)
    if nx.is_chordal(G_unmarked):
        draw_four_complete_graph(G_unmarked, G_c.pos, G_c.full_pos)
        raise Exception("Haven't handled chordal graph! ")
        # TODO -> update the co.chords variable for each node and all its nbs
    # otherwise do nothing..


# TODO collapse entry..
def initialize_canonical_order(_G: nx.Graph, pos, full_pos):
    # TODO -> test that graph is 4TP
    G = deepcopy(_G).to_undirected()
    G_c = G_canonical(G, pos, full_pos)
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
    update_chords(G_c, co)
    co.decrement_k()

    # no vertices will yet have up to two neighbors, so pick v_w
    # TODO check (v_w is valid, check 1 and 2.1)
    co.vertices[co.x].is_marked = True
    co.vertices[co.w].ordered_number = co.k
    update_neighbors_visited(G, co, co.x)
    update_chords(G_c, co)
    co.decrement_k()

    # check the graph is ok at this point... 

    # now should have 1 potential nb
    assert len(co.potential_vertices()) == 1

    return G_c, co


def iterate_canonical_order(G_c: G_canonical, co: CanonicalOrder):
    count = 0
    while co.k > 4:
        potential = co.potential_vertices()
        if len(potential) == 0:
            raise Exception(f"No potential vertices: {co.show_vertices()}")
        if len(potential) > 1:
            raise Exception(
                f"Multiple potential: {[i.name for i in potential]}. Would choose {potential[0].name}.  {co.show_vertices()}"
            )

        vk = potential[0]

        is_Gk_minus_1_biconnected(G_c.G, co)
        are_u_v_in_Ck(G_c, co)
        # TODO assert vk is valid
        co.vertices[vk.name].is_marked = True
        co.vertices[vk.name].ordered_number = co.k
        update_neighbors_visited(G_c.G, co, vk.name)
        update_chords(G_c, co)
        co.decrement_k()

        count+=1


    return G_c, co
