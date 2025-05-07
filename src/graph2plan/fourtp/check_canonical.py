from graph2plan.dcel.original import create_embedding
from graph2plan.dual.helpers import split_cardinal_and_interior_edges
from graph2plan.fourtp.canonical_order import CanonicalOrder
from copy import deepcopy


import networkx as nx

from graph2plan.helpers.geometry_interfaces import VertexPositions


def is_Gk_minus_1_biconnected(G: nx.Graph, co: CanonicalOrder):
    assert len(co.Gk_minus_1) >= 3, "Need at least three vertices to check biconnection"
    Gk_minus_1 = G.subgraph(co.Gk_minus_1)
    assert nx.is_biconnected(Gk_minus_1)


# TODO this all goes elsewhere..
def print_all_cw_nbs(PE: nx.PlanarEmbedding, node: str):
    print(f"cw nbs of {node}: {list(PE.neighbors_cw_order(node))}")


def get_first_cw_nb(PE: nx.PlanarEmbedding, node: str):
    return list(PE.neighbors_cw_order(node))[0]


def get_last_cw_nb(PE: nx.PlanarEmbedding, node: str):
    return list(PE.neighbors_cw_order(node))[-1]


def get_embedding_of_four_complete_G(G: nx.Graph, full_pos: VertexPositions):
    card, inte = split_cardinal_and_interior_edges(G)
    PE = create_embedding(nx.edge_subgraph(G, inte), full_pos)
    return PE


# TODO use CDE class names 
def add_cw_pair(PE: nx.PlanarEmbedding, n="v_n", e="v_e"):
    # e = "v_e"
    # n = "v_n"
    print("-- add first half edge ---")
    PE.add_half_edge_ccw(n, e, reference_neighbor=get_first_cw_nb(PE, n))
    print_all_cw_nbs(PE, n)
    print_all_cw_nbs(PE, e)
    print("-- add second half edge ---")
    PE.add_half_edge_cw(e, n, reference_neighbor=get_last_cw_nb(PE, e))
    print_all_cw_nbs(PE, n)
    print_all_cw_nbs(PE, e)
    
    return PE
    # want to check that the added vertex is either first or last..

def add_exterior_embed(_PE: nx.PlanarEmbedding):
    PE = deepcopy(_PE)
    PE = add_cw_pair(PE)
    PE = add_cw_pair(PE, "v_e", "v_s")
    PE = add_cw_pair(PE, "v_s", "v_w")
    PE = add_cw_pair(PE, "v_w", "v_n")
    PE = add_cw_pair(PE, "v_n", "v_s")
    PE.check_structure()

    return PE
    



def are_u_v_in_Ck(G: nx.Graph, co: CanonicalOrder):
    assert (
        co.u in co.Gk and co.v in co.Gk
    )  # TODO need to be in external face! need to calculate an embedding!


def do_vk_nbs_form_2v_subinterval_in_Ck_minus_1():
    pass


def does_vk_have_2plus_nbs_in_G_diff_Gk_minus_1():
    pass
