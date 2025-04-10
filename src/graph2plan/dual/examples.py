from typing import Literal
import networkx as nx

from graph2plan.dcel.create import create_embedding
from graph2plan.dual.check import check_correct_n_faces_in_edge_face_dict
from graph2plan.dual.create_dual import create_dual, prep_dual
from graph2plan.dual.create_rectangle import calculate_domains, calculate_x_domains
from graph2plan.dual.interfaces import VertexDomain, Domain, Domains
from graph2plan.external_embed.main import fully_embed_graph, EmbedResult
from graph2plan.external_embed.naive import (
    embed_other_source,
    embed_other_target,
    embed_target_source_edge,
)
from ..helpers.general_interfaces import Coordinate, ShapelyBounds, VertexPositions
from ..dcel.interfaces import T
from sympy import Polygon
from copy import deepcopy

"""
    example from Kant+He'97
"""


def assign_pos_w_cardinal(arrs: list[list[T]]) -> VertexPositions:
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

    return VertexPositions({k: v.pair for k, v in pos.items()})


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


def naive_embed_kant():
    # TODO -> need to embed north south..
    G, pos = kant_G1()
    directed_edges = list(G.edges)
    PG = create_embedding(G, pos)
    PG1, de1 = embed_other_target(PG)
    PG2, de2 = embed_other_source(PG1)
    PG3, de3 = embed_target_source_edge(PG2)
    print("\nnaive")
    print(f"==>> PG: {len(PG.edges)}")
    print(f"==>> PG1: {len(PG1.edges)}")
    print(f"==>> PG2: {len(PG2.edges)}")
    print(f"==>> PG3: {len(PG3.edges)}")

    return EmbedResult(PG3, pos, sorted(directed_edges + de1 + de2 + de3))

    # PG_complete.check_structure()
    # return PG_complete, pos


def compare_embeds():
    r1, _ = fully_embed_kant()
    n1 = naive_embed_kant()

    r1_faces = prep_dual(r1.embedding, r1.directed_edges)
    print("r1 - proper embedding")
    check_correct_n_faces_in_edge_face_dict(r1_faces)
    dual_graph, dual_pos = create_dual(r1_faces, r1.pos)

    print("n1 - naive embedding")
    n1_faces = prep_dual(n1.embedding, n1.directed_edges)
    check_correct_n_faces_in_edge_face_dict(n1_faces)
    dual_graph, dual_pos = create_dual(n1_faces, n1.pos)
    return r1, n1, r1_faces, n1_faces


def test_dual_for_proper_embed():
    r1, _ = fully_embed_kant()
    r1.draw()
    r1_faces = prep_dual(r1.embedding, r1.directed_edges)
    print("r1 - proper embedding")
    check_correct_n_faces_in_edge_face_dict(r1_faces)
    dual_graph, dual_pos = create_dual(r1_faces, r1.pos, "y")
    x_domains = calculate_domains(dual_graph, r1.embedding, r1.directed_edges, "y")

    return r1, r1_faces, x_domains

def test_dual_for_proper_embed2():
    _, r1 = fully_embed_kant()
    r1.draw()
    r1_faces = prep_dual(r1.embedding, r1.directed_edges)
    print("r1 - proper embedding")
    check_correct_n_faces_in_edge_face_dict(r1_faces)
    dual_graph, dual_pos = create_dual(r1_faces, r1.pos, "x")
    y_domains = calculate_domains(dual_graph, r1.embedding, r1.directed_edges, "x")
    # TODO calculate_y_domains

    return r1, r1_faces, y_domains


def merge_domains(x_domains: dict[str, VertexDomain], y_domains: dict[str, VertexDomain]):
    # r2, r2_faces, y_domains = test_dual_for_proper_embed2()
    # r1, r1_faces, x_domains = test_dual_for_proper_embed()
    domains = []
    assert x_domains.keys() == y_domains.keys()
    for key in x_domains.keys():
        xdom = x_domains[key]
        ydom = y_domains[key]
        domains.append(Domain(name=key, bounds=ShapelyBounds(min_x=xdom.min, min_y=ydom.min, max_x=xdom.max, max_y=ydom.max)))

    doms =  Domains(domains)
    doms.draw()

    return doms

