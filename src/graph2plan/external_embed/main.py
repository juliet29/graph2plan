from typing import Any, Literal, NamedTuple

from networkx import NetworkXError, NetworkXException
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
    # plt.figure()
    # nx.draw_networkx(PG1.to_directed(), pos1)
    return G1, PG1, pos1, new_edges



def embed_target_source_edge(_PG: nx.PlanarEmbedding, axis: Axis = "y"):
    assn = assignments[axis]
    PG = deepcopy(_PG)


    if axis == "y":
        PG.add_half_edge_ccw(assn.source, assn.target, reference_neighbor=assn.other_source)
    else: 
        PG.add_half_edge_cw(assn.source, assn.target, reference_neighbor=assn.other_source)
    source_nbs = list(PG.neighbors_cw_order(assn.source))
    assert source_nbs[0] == assn.target or source_nbs[-1] == assn.target

    if axis == "y":
        PG.add_half_edge_cw(assn.target, assn.source, reference_neighbor=assn.other_source)
    else:
        PG.add_half_edge_ccw(assn.target, assn.source, reference_neighbor=assn.other_source)
    target_nbs = list(PG.neighbors_cw_order(assn.target))
    assert target_nbs[0] == assn.source or target_nbs[-1] == assn.source

    directed_edges = [(assn.source, assn.target)]
    soft_check_structure(PG)
    return PG, directed_edges

    # check outer face, area should be opposite of if traverse other way




class EmbedResult(NamedTuple):
    embedding: nx.PlanarEmbedding
    pos: VertexPositions
    directed_edges: list[tuple[Any, Any]]

    def draw(self):
        plt.figure()
        nx.draw_networkx(nx.DiGraph(self.directed_edges), self.pos)


def fully_embed_graph(G:nx.Graph,  pos: VertexPositions,  axis: Axis):
    directed_edges = list(G.edges)
    PG = create_embedding(G, pos)
    _, PG1, pos1, new_edges1 = add_other_vertices(G, PG, pos, axis)
    PG2, new_edges2 = embed_target_source_edge(PG1, axis)
    return EmbedResult(PG2, pos1, directed_edges + new_edges1 + new_edges2)



def fully_embed_kant():
    res1 = fully_embed_graph(*kant_G1(), "y")
    res1.draw()
    res2 = fully_embed_graph(*kant_G2(), "x")
    res2.draw()


