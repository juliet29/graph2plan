from graph2plan.dcel.interfaces import EdgeList
from graph2plan.fourtp.canonical_interfaces import (
    CanonicalOrder,
    G_canonical,
    set_difference,
)


import networkx as nx

from graph2plan.helpers.utils import neighborhood


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


def first_and_second_nbs(G, node):
    # this is an unfiltered G
    return neighborhood(G, node, 1) + neighborhood(G, node, 2)


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


def check_and_update_chords(G_c: G_canonical, co: CanonicalOrder, node: str):
    G_unmarked = G_c.G.subgraph(co.unmarked)
    if nx.is_chordal(G_unmarked):
        # G_c.draw(co.unmarked)
        # print(f"outer face of unmarked: {G_c.outer_face_of_unmarked(co)}")
        update_chords(G_c, co, node)


def update_neighbors_visited(G: nx.Graph, co: CanonicalOrder, vertex_name):
    nbs = G.neighbors(vertex_name)

    nbs_to_update = [i for i in nbs if not co.vertices[i].is_marked]
    # print(f"updating nbs of vertex {vertex_name}: {nbs_to_update}")
    for nb in nbs_to_update:
        co.vertices[nb].n_marked_nbs += 1
