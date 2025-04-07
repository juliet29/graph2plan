from typing import Literal
import networkx as nx

from graph2plan.dcel.create import create_embedding
from graph2plan.external_embed.main import fully_embed_graph
from ..helpers.general_interfaces import Coordinate, VertexPositions
from ..dcel.interfaces import T
from sympy import Polygon
from copy import deepcopy

"""
    example from Kant+He'97
"""


def assign_pos_w_cardinal(arrs: list[list[T]]):
    max_len = max([len(i) for i in arrs])
    n_arrs = len(arrs)

    pos = {}
    default_y = n_arrs / 2
    default_x = max_len / 2
    init_x = 0
    init_y = 0
    del_x = init_x + 1
    del_y = init_y + 1

    # TODO remove- no longer being assigned here.. 

    pos["v_w"] = Coordinate(init_x, default_y)
    pos["v_e"] = Coordinate(max_len + del_x + 1, default_y)

    pos["v_s"] = Coordinate(default_x, init_y)
    pos["v_n"] = Coordinate(default_x, n_arrs + del_y)

    for level, arr in enumerate(arrs):
        shift = 1 if level % 2 else 0
        for ix, vertex in enumerate(arr):
            x = ix + del_x + shift
            y = level + del_y
            pos[vertex] = Coordinate(x, y)

    return {k: v.pair for k, v in pos.items()}


def kant_G1():
    l1 = ["i", "e", "c", "h"]
    l2 = ["f", "d", "b"]
    l3 = ["j", "a", "g"]
    arrs = [l1, l2, l3]

    l1_edges = [("v_s", i) for i in l1]  # + ["v_w", "v_e"]
    l2_edges = [("i", "j"), ("e", "f"), ("c", "d"), ("c", "b"), ("h", "b")]
    l3_edges = [("f", "a"), ("d", "a"), ("b", "a"), ("b", "g")]
    l4_edges = [(i, "v_n") for i in l3]  # + ["v_w", "v_e"]

    G = nx.DiGraph()
    G.add_edges_from(l1_edges + l2_edges + l3_edges + l4_edges)  # +  final_edge

    # TODO check is st
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
    G.add_edges_from(
        l1_edges + l2_edges + l3_edges + l4_edges + l5_edges
    )  # +  final_edge
    return G, assign_pos_w_cardinal(arrs)


def fully_embed_kant():
    res1 = fully_embed_graph(*kant_G1(), "y")
    # res1.draw()
    res2 = fully_embed_graph(*kant_G2(), "x")
    # res2.draw()

    return res1, res2

    # PG_complete.check_structure()
    # return PG_complete, pos
