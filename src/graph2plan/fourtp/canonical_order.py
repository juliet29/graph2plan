from copy import deepcopy
from typing import Union
import networkx as nx

from graph2plan.dcel.interfaces import EdgeList
from graph2plan.helpers.utils import neighborhood
from .check_canonical import is_Gk_minus_1_biconnected, are_u_v_in_Ck


from graph2plan.fourtp.canonical_interfaces import (
    CanonicalOrder,
    G_canonical,
    NotImplementedError,
    VertexData,
    set_difference,
)
from .draw_four_complete import draw_four_complete_graph
from ..dcel.original import create_embedding


def update_neighbors_visited(G: nx.Graph, co: CanonicalOrder, vertex_name):
    nbs = G.neighbors(vertex_name)

    nbs_to_update = [i for i in nbs if not co.vertices[i].is_marked]
    print(f"updating nbs of vertex {vertex_name}: {nbs_to_update}")
    for nb in nbs_to_update:
        co.vertices[nb].n_marked_nbs += 1


def first_and_second_nbs(G, node):
    # this is an unfiltered G
    return neighborhood(G, node, 1) + neighborhood(G, node, 2)


def find_chords(G_c: G_canonical, co: CanonicalOrder):
    C_unmarked = nx.cycle_graph(G_c.outer_face_of_unmarked(co), nx.Graph)

    G_unmarked = G_c.G.subgraph(co.unmarked)
    # only care about nodes that are on the outer cycle
    G_unmarked_cyle_nodes = G_unmarked.subgraph(C_unmarked.nodes)

    chords = set_difference(
        EdgeList.to_edge_list(G_unmarked_cyle_nodes.edges).edges,
        EdgeList.to_edge_list(C_unmarked.edges).edges,
    )

    return [e.pair for e in chords]


def update_chords(G_c: G_canonical, co: CanonicalOrder, node):
    nbs = first_and_second_nbs(G_c.G, node) # that are unmarked
    unmarked_nbs = [nb for nb in nbs if not co.vertices[nb].is_marked]
    chords = find_chords(G_c, co)
    # set all chords of relevant nbs to 0
    for nb in nbs:
        co.vertices[nb].n_chords = 0
    
    # then update as they come up in edges.. 
    for chord in chords:
        for vertex in chord:
            if vertex in unmarked_nbs:
                co.vertices[vertex].n_chords +=1

    non_zero_chords = [i for i in co.vertices.values() if i.n_chords > 0]
    print(f"==>> non_zero_chords: {non_zero_chords}")


def check_and_update_chords(G_c: G_canonical, co: CanonicalOrder, node):
    G_unmarked = G_c.G.subgraph(co.unmarked)
    if nx.is_chordal(G_unmarked):
        G_c.draw(co.unmarked)
        print(f"outer face of unmarked: {G_c.outer_face_of_unmarked(co)}")
        update_chords(G_c, co, node)
        

        # draw_four_complete_graph(G_unmarked, G_c.pos, G_c.full_pos)
        # raise NotImplementedError("Haven't handled chordal graph! ")

        # TODO -> update the co.chords variable for each node and all its nbs
        # also reflect fact that some may have 0 chords..
    # otherwise do nothing..


# TODO collapse entry..
def initialize_canonical_order(_G: nx.Graph, pos, full_pos):
    # TODO -> test that graph is 4TP
    G = deepcopy(_G).to_undirected()
    G_c = G_canonical(G, pos, full_pos)
    vertices = {i: VertexData(i) for i in G.nodes}
    co = CanonicalOrder(vertices, u="v_s", v="v_e", w="v_n", x="v_w", n=G.order())

    # mark and order the starting nodes, but dont update their nbs
    co.vertices[co.u].is_marked = True
    co.vertices[co.v].is_marked = True
    co.vertices[co.u].ordered_number = 1
    co.vertices[co.v].ordered_number = 2
    update_neighbors_visited(G, co, co.u)
    update_neighbors_visited(G, co, co.v)

    # set v_n(orth), and v_w to be v_n and v_n-1, and update their nbs
    # TODO check v_n(orth) is valid, check 1 only

    co.vertices[co.w].n_marked_nbs = 2
    co.vertices[co.w].is_marked = True
    co.vertices[co.w].ordered_number = co.n
    # update_neighbors_visited(G, co, co.w)
    # update_chords(G_c, co)
    # co.decrement_k()

    # # no vertices will yet have up to two neighbors, so pick v_w
    # # TODO check (v_w is valid, check 1 and 2.1)
    # co.vertices[co.x].is_marked = True
    # co.vertices[co.w].ordered_number = co.k
    # update_neighbors_visited(G, co, co.x)
    # update_chords(G_c, co)
    # co.decrement_k()

    # check the graph is ok at this point...

    # now should have 1 potential nb
    # co.potential_vertices()
    assert len(co.potential_vertices()) == 1

    return G_c, co


def iterate_canonical_order(G_c: G_canonical, co: CanonicalOrder):
    count = 0
    print(co.k, co.n)
    while co.k < co.n:
        potential = co.potential_vertices()
        if len(potential) == 0:
            raise Exception(f"No potential vertices: {co.show_vertices()}")
        if len(potential) > 1:
            print(
                f"Multiple potential: {[i.name for i in potential]}. Choosing {potential[0].name}"
            )

        vk = potential[0]

        try:
            co.vertices[vk.name].ordered_number = co.k
            # test choice of vk produces valid graph..
            is_Gk_minus_1_biconnected(G_c.G, co)
            are_u_v_in_Ck(G_c, co)
        except:
            raise Exception(f"ordering {vk.name} failed..")
        # TODO one more check!

        co.vertices[vk.name].is_marked = True

        update_neighbors_visited(G_c.G, co, vk.name)
        check_and_update_chords(G_c, co, vk)
        co.increment_k()

        count += 1

        if count > 2:
            print("breaking.. ")
            break

    return G_c, co
