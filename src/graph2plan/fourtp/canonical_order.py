from copy import deepcopy
import functools

from matplotlib import pyplot as plt
import networkx as nx

from graph2plan.dcel.interfaces import CanonicalOrderingFailure, EdgeList
from graph2plan.fourtp.canonical_interfaces import (
    CanonicalOrder,
    G_canonical,
    VertexData,
    set_difference,
)
from graph2plan.helpers.geometry_interfaces import VertexPositions
from graph2plan.helpers.utils import neighborhood

from .check_canonical import vk_permits_valid_order


def update_neighbors_visited(G: nx.Graph, co: CanonicalOrder, vertex_name):
    nbs = G.neighbors(vertex_name)

    nbs_to_update = [i for i in nbs if not co.vertices[i].is_marked]
    # print(f"updating nbs of vertex {vertex_name}: {nbs_to_update}")
    for nb in nbs_to_update:
        co.vertices[nb].n_marked_nbs += 1


# TODO move chords stuff elsewehere.. 
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


def update_chords(G_c: G_canonical, co: CanonicalOrder, node: str):
    # TODO this could be cleaner if has a Gk-1..
    nbs = first_and_second_nbs(G_c.G, node)  # that are unmarked
    unmarked_nbs = [nb for nb in nbs if not co.vertices[nb].is_marked]
    chords = find_chords(G_c, co)
    # set all chords of relevant nbs to 0
    for nb in nbs:
        co.vertices[nb].n_chords = 0

    # then update as they come up in edges..
    for chord in chords:
        for vertex in chord:
            if vertex in unmarked_nbs:
                co.vertices[vertex].n_chords += 1

    # non_zero_chords = {
    #     i.name: i.n_chords for i in co.vertices.values() if i.n_chords > 0
    # }
    # print(f"==>> non_zero_chords: {non_zero_chords}")


def check_and_update_chords(G_c: G_canonical, co: CanonicalOrder, node: str):
    G_unmarked = G_c.G.subgraph(co.unmarked)
    if nx.is_chordal(G_unmarked):
        # G_c.draw(co.unmarked)
        # print(f"outer face of unmarked: {G_c.outer_face_of_unmarked(co)}")
        update_chords(G_c, co, node)


# TODO collapse entry..
def initialize_canonical_order(_G: nx.Graph, pos, full_pos):
    # TODO -> test that graph is 4TP
    G = deepcopy(_G).to_undirected()
    G_c = G_canonical(G, pos, full_pos)
    vertices = {i: VertexData(i) for i in G.nodes}
    co = CanonicalOrder(vertices, u="v_w", v="v_s", w="v_n", n=G.order())

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
            raise Exception(f"While iterating, ordering {vk.name} failed.. time to try breadth-first search?")

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


