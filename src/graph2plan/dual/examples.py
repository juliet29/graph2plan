from typing import Literal
import networkx as nx
from ..dcel.interfaces import Coordinate, T, VertexPositions
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

    final_edge = [("v_s", "v_n")]

    G = nx.DiGraph()
    G.add_edges_from(l1_edges + l2_edges + l3_edges + l4_edges)  # +  final_edge

    return G, assign_pos_w_cardinal(arrs)


# TODO check is st


def get_outer_face_st_graph(
    PG: nx.PlanarEmbedding, pos: VertexPositions, source: Literal["v_s", "v_w"] = "v_s"
):
    def get_polygon_area(face: list):
        p = Polygon(*[pos[i] for i in face])
        assert isinstance(p, Polygon)
        return p.area

    PG.check_structure()
    source_neighbors = list(PG.neighbors_cw_order(source))
    ccw_edge = (source, source_neighbors[-1])
    outer_face = PG.traverse_face(*ccw_edge)

    # check using area
    inner_face = PG.traverse_face(ccw_edge[1], ccw_edge[0])
    outer_area, inner_area = [get_polygon_area(i) for i in (outer_face, inner_face)]
    if inner_area < 1:
        assert outer_area > 1
    else:
        assert outer_area < 1

    return outer_face


def embed_other_target(_PG: nx.PlanarEmbedding, vertex="v_e"):
    # outer_face  = get_outer_face_st_graph(PG, pos)
    # start w v_e
    # TODO s
    source, target = "v_s", "v_n"

    PG = deepcopy(_PG)
    ref = list(PG.neighbors_cw_order(source))[-1]
    PG.add_half_edge_cw(source, vertex, reference_neighbor=ref)
    PG.add_half_edge_first(vertex, source)
    

    ref = list(PG.neighbors_cw_order(target))[0]
    PG.add_half_edge_ccw(vertex, target, reference_neighbor=source)
    PG.add_half_edge_ccw(target, vertex, reference_neighbor=ref)

    assert list(PG.neighbors_cw_order(target))[0] == vertex
    PG.check_structure()
    return PG


def embed_other_source(_PG: nx.PlanarEmbedding, vertex="v_w"):
    source, target = "v_s", "v_n"

    PG = deepcopy(_PG)

    ref = list(PG.neighbors_cw_order(source))[0]
    print(ref)
    PG.add_half_edge_ccw(source, vertex, reference_neighbor=ref)
    PG.add_half_edge_first(vertex, source)
    assert list(PG.neighbors_cw_order(source))[0] == vertex

    print(list(PG.neighbors_cw_order(source)))

    ref = list(PG.neighbors_cw_order(target))[-1]
    
    PG.add_half_edge_cw(target, vertex, reference_neighbor=ref)
    print(f"{target} nbs: {list(PG.neighbors_cw_order(target))}")

    PG.add_half_edge_cw(vertex, target, reference_neighbor=source)
    print(f"{vertex} nbs: {list(PG.neighbors_cw_order(vertex))}")




    PG.check_structure()
    return PG



    # check outer face, area should be opposite of if traverse other way
