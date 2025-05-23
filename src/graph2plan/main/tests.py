from graph2plan.dual.create_rectangular_floorplan import create_floorplan_from_st_graphs
from graph2plan.fourtp.faces import get_embedding_of_four_complete_G
from graph2plan.rel.draw_rel import plot_rel_base_graph
from graph2plan.rel.rel2 import create_rel_and_extract_st_graphs, initialize_rel_graph
from ..canonical.canonical_interfaces import (
    read_canonical_outputs,
    write_canonical_outputs,
)
from ..canonical.canonical_order import (
    create_canonical_order
)
from ..fourtp.four_complete import (
    four_complete,
)
from .examples import kk85, kk85_outer_face


def test_four_complete_kk85():
    G, pos = kk85()
    G, full_pos = four_complete(G, pos, kk85_outer_face())
    # full_pos = place_cardinal(pos, path_pairs)
    return G, pos, full_pos


def test_co_kk85():
    G, pos = kk85()
    G, full_pos = four_complete(G, pos, kk85_outer_face())
    return create_canonical_order(G, pos, full_pos)

def write_co_kk85():
    G_c, co = test_co_kk85()
    write_canonical_outputs(G_c, co)


# def test_co_three_graph():
#     G, pos = create_integer_G_and_pos(nx.triangular_lattice_graph(1, 1))
#     Gfc, full_pos = graph_to_four_complete(G, pos)
#     print(Gfc.nodes)
#     G_c, co = initialize_canonical_order(Gfc, pos, full_pos)
#     G_c, co = iterate_canonical_order(G_c, co)
#     return G_c, co

def test_init_rel():
    # assuming that are reading from an existing co ->
    # TODO in reality, need to cache 
    G, co_vertices, pos = read_canonical_outputs()
    Grel = initialize_rel_graph(G, co_vertices)
    plot_rel_base_graph(Grel, pos, co_vertices)
    return Grel

def test_assign_rel():
    G, co_vertices, pos = read_canonical_outputs()
    embedding = get_embedding_of_four_complete_G(G, pos)
    Grel, T1, T2 = create_rel_and_extract_st_graphs(G, co_vertices, embedding)
    plot_rel_base_graph(Grel, pos, co_vertices, (T1, T2))
    return Grel, T1, T2 


def test_create_dual():
    G, co_vertices, pos = read_canonical_outputs()
    embedding = get_embedding_of_four_complete_G(G, pos)
    _, T1, T2 = create_rel_and_extract_st_graphs(G, co_vertices, embedding)
    merged_doms = create_floorplan_from_st_graphs(T1, T2, pos)
    return merged_doms






# def triangular_graph_to_dual(G):
#     Ginteger, pos = create_integer_G_and_pos(G)
#     G_four_complete, path_pairs = graph_to_four_complete(Ginteger, pos)
