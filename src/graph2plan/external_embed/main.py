from typing import Literal
from graph2plan.dcel.create import create_embedding, extend_embedding, soft_check_structure
from graph2plan.dcel.interfaces import transform_graph_egdes
from graph2plan.helpers.general_interfaces import (
    CoordinateList,
    ShapelyBounds,
    VertexPositions,
)
from graph2plan.helpers.general_interfaces import assignments, Axis
from ..dual.examples import kant_G1, kant_G2
import networkx as nx
from shapely import MultiPoint
from copy import deepcopy
from .outer_face import get_outer_face_st_graph, split_outer_face
import matplotlib.pyplot as plt
from functools import partial


def create_bounding_ellipse(_G: nx.Graph, _pos: VertexPositions):
    pos = deepcopy(_pos)
    G = deepcopy(_G)
    points = MultiPoint([p for p in pos.values()])
    bounds = ShapelyBounds(*points.envelope.bounds)
    new_pos = bounds.circular_cardinal_values()._asdict()
    pos_extension = dict(set(new_pos.items()) - set(pos.items()))
    G.add_nodes_from(pos_extension.keys())
    pos.update(pos_extension)
    return G, pos


def add_other_vertices(
    G: nx.Graph,
    PG: nx.PlanarEmbedding,
    pos: VertexPositions,
    axis: Axis = "y"
):
    assn = assignments[axis]
    G1, pos1 = create_bounding_ellipse(G, pos)
    outer_face = get_outer_face_st_graph(PG, pos, assn.source)
    split = partial(split_outer_face, outer_face, assn.source, assn.target)

    if axis == "y":
        other_source_nbs, other_target_nbs = split()
    elif axis == "x":
        other_target_nbs, other_source_nbs = split()

    new_edges = [(assn.other_source, i) for i in other_source_nbs] + [
        (i, assn.other_target) for i in other_target_nbs
    ]
    # print(f"==>> new_edges: {new_edges}")
    
    G1.add_edges_from(new_edges)
    PG1 = extend_embedding(G1, PG, pos1)
    plt.figure()
    nx.draw_networkx(PG1.to_directed(), pos1)
    return G1, PG1, pos1, new_edges



def embed_target_source_edge(_PG: nx.PlanarEmbedding, axis: Axis = "y"):
    assn = assignments[axis]
    PG = deepcopy(_PG)
    # other_source = "v_w"
    # print(f"{assn.source} cw: {list(PG.neighbors_cw_order(assn.source))}")
    if axis == "y":
        PG.add_half_edge_ccw(assn.source, assn.target, reference_neighbor=assn.other_source)
    else: 
        PG.add_half_edge_cw(assn.source, assn.target, reference_neighbor=assn.other_source)
    source_nbs = list(PG.neighbors_cw_order(assn.source))
    # target should be at end or beginning 
    assert source_nbs[0] == assn.target or source_nbs[-1] == assn.target
    # print(f"{assn.source} cw after: {list(PG.neighbors_cw_order(assn.source))}")

    # print(f"{assn.target} cw: {list(PG.neighbors_cw_order(assn.target))}")
    if axis == "y":
        PG.add_half_edge_cw(assn.target, assn.source, reference_neighbor=assn.other_source)
    else:
        PG.add_half_edge_ccw(assn.target, assn.source, reference_neighbor=assn.other_source)

    target_nbs = list(PG.neighbors_cw_order(assn.target))
    assert target_nbs[0] == assn.source or target_nbs[-1] == assn.source

    # print(f"{assn.target} cw after: {list(PG.neighbors_cw_order(assn.target))}")


    directed_edges = [(assn.source, assn.target)]

    soft_check_structure(PG)
    return PG, directed_edges

    # check outer face, area should be opposite of if traverse other way



def test():
    G, pos = kant_G1()
    PG = create_embedding(G, pos)
    G1, PG1, pos1, new_edges = add_other_vertices(G, PG, pos, "y")
    PG2,_ = embed_target_source_edge(PG1, "y")
    plt.figure()
    nx.draw_networkx(PG2.to_directed(), pos)

    return G1, PG1, pos1


def test2():
    G, pos = kant_G2()
    # nx.draw_networkx(G, pos)
    PG = create_embedding(G, pos)
    G1, PG1, pos1, new_edges = add_other_vertices(G, PG, pos, "x")
    PG2,_ = embed_target_source_edge(PG1, "x")
    plt.figure()
    nx.draw_networkx(PG2.to_directed(), pos)

    return G1, PG1, pos1
