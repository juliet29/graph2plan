from typing import Literal
import networkx as nx

from graph2plan.dcel.create import create_embedding
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


def embed_other_target(_PG: nx.PlanarEmbedding, vertex="v_e"):
    # TODO s
    _PG.check_structure()
    source, target = "v_s", "v_n"

    PG = deepcopy(_PG)
    ref = list(PG.neighbors_cw_order(source))[-1]
    PG.add_half_edge_cw(source, vertex, reference_neighbor=ref)
    PG.add_half_edge_first(vertex, source)
    PG.check_structure()

    ref = list(PG.neighbors_cw_order(target))[0]
    PG.add_half_edge_ccw(vertex, target, reference_neighbor=source)
    PG.add_half_edge_ccw(target, vertex, reference_neighbor=ref)
    PG.check_structure()

    directed_edges = [(source, vertex), (vertex, target)]
    return PG, directed_edges


def embed_other_source(_PG: nx.PlanarEmbedding, vertex="v_w"):
    _PG.check_structure()
    source, target = "v_s", "v_n"

    PG = deepcopy(_PG)

    ref = list(PG.neighbors_cw_order(source))[0]
    PG.add_half_edge_ccw(source, vertex, reference_neighbor=ref)
    PG.add_half_edge_first(vertex, source)
    PG.check_structure()

    ref = list(PG.neighbors_cw_order(target))[-1]
    PG.add_half_edge_cw(target, vertex, reference_neighbor=ref)
    PG.add_half_edge_cw(vertex, target, reference_neighbor=source)
    PG.check_structure()

    directed_edges = [(source, vertex), (vertex, target)]
    return PG, directed_edges


def embed_target_source_edge(_PG: nx.PlanarEmbedding, source="v_s", target="v_n"):
    PG = deepcopy(_PG)
    other_source = "v_w"
    # print(f"{source} cw: {list(PG.neighbors_cw_order(source))}")
    PG.add_half_edge_ccw(source, target, reference_neighbor=other_source)
    # print(f"{source} cw after: {list(PG.neighbors_cw_order(source))}")

    # print(f"{target} cw: {list(PG.neighbors_cw_order(target))}")
    PG.add_half_edge_cw(target, source, reference_neighbor=other_source)
    # print(f"{target} cw after: {list(PG.neighbors_cw_order(target))}")
    directed_edges = [(source, target)]

    PG.check_structure()
    return PG, directed_edges

    # check outer face, area should be opposite of if traverse other way


def embedded_kant_G1():
    # TODO -> need to embed north south..
    G, pos = kant_G1()
    directed_edges = list(G.edges)
    PG = create_embedding(G, pos)
    PG1, de1 = embed_other_target(PG)
    PG2, de2 = embed_other_source(PG1)
    PG3, de3 = embed_target_source_edge(PG2)

    return PG3, pos, directed_edges + de1 + de2 + de3

    # PG_complete.check_structure()
    # return PG_complete, pos
