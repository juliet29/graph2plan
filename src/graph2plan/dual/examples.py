import networkx as nx

from ..dcel.external import fully_embed_graph
from ..dcel.interfaces import T
from ..helpers.geometry_interfaces import Coordinate, VertexPositions
from .create_rectangle import create_dual_and_calculate_domains

"""
    example from Kant+He'97
"""


def assign_pos_w_cardinal(arrs: list[list[T]]) -> VertexPositions:
    max_len = max([len(i) for i in arrs])
    n_arrs = len(arrs)

    pos = {}
    default_y = n_arrs / 2
    default_x = max_len / 2
    init_x = init_y = 0
    delta_x = delta_y = 1

    # TODO think about removing...

    pos["v_w"] = Coordinate(init_x, default_y)
    pos["v_e"] = Coordinate(max_len + delta_x + 1, default_y)

    pos["v_s"] = Coordinate(default_x, init_y)
    pos["v_n"] = Coordinate(default_x, n_arrs + delta_y)

    for level, arr in enumerate(arrs):
        shift = 1 if level % 2 else 0
        for ix, vertex in enumerate(arr):
            x = ix + delta_x + shift
            y = level + delta_y
            pos[vertex] = Coordinate(x, y)

    return VertexPositions({k: v.pair for k, v in pos.items()})


def kant_G1():
    l1 = ["i", "e", "c", "h"]
    l2 = ["f", "d", "b"]
    l3 = ["j", "a", "g"]
    arrs = [l1, l2, l3]

    l1_edges = [("v_s", i) for i in l1] 
    l2_edges = [("i", "j"), ("e", "f"), ("c", "d"), ("c", "b"), ("h", "b")]
    l3_edges = [("f", "a"), ("d", "a"), ("b", "a"), ("b", "g")]
    l4_edges = [(i, "v_n") for i in l3] 

    G = nx.DiGraph()
    G.add_edges_from(l1_edges + l2_edges + l3_edges + l4_edges)  # +  final_edge
    return G, assign_pos_w_cardinal(arrs)


def kant_G2():
    l1 = ["i", "e", "c", "h"]
    l2 = ["f", "d", "b"]
    l3 = ["j", "a", "g"]
    arrs = [l1, l2, l3]

    l1_edges = [("v_w", i) for i in ("i", "j")]
    l2_edges = [("i", "e"), ("e", "d"), ("e", "c"), ("c", "h")]
    l3_edges = [("j", "e"), ("j", "f"), ("f", "d"), ("d", "b")]
    l4_edges = [("j", "a"), ("a", "g")]
    l5_edges = [(i, "v_e") for i in ("g", "b", "h")]

    G = nx.DiGraph()
    G.add_edges_from(l1_edges + l2_edges + l3_edges + l4_edges + l5_edges)
    return G, assign_pos_w_cardinal(arrs)


def fully_embed_kant():
    res1 = fully_embed_graph(*kant_G1(), "y")
    res2 = fully_embed_graph(*kant_G2(), "x")
    return res1, res2


def create_domains_for_kant(draw=False):
    r1, r2 = fully_embed_kant()
    x_domains = create_dual_and_calculate_domains(r1, "y", draw)
    y_domains = create_dual_and_calculate_domains(r2, "x", draw)
    return x_domains, y_domains
