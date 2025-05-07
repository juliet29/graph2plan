from copy import deepcopy

import networkx as nx
from shapely import MultiPoint

from ..helpers.geometry_interfaces import (
    ShapelyBounds,
    VertexPositions,
)
from ..helpers.graph_interfaces import Axis, assignments
from .interfaces import EmbedResult, transform_graph_egdes
from .original import (
    create_embedding,
    handle_half_edge,
    soft_check_structure,
)


def create_bounding_ellipse(_G: nx.Graph, _pos: VertexPositions):
    pos = deepcopy(_pos)
    G = deepcopy(_G)
    points = MultiPoint([p for p in pos.values()])
    bounds = ShapelyBounds(*points.envelope.bounds) # TODO this is repeated elsewhere.. 
    new_pos = bounds.circular_cardinal_values()._asdict()
    pos_extension = dict(set(new_pos.items()) - set(pos.items()))
    G.add_nodes_from(pos_extension.keys())
    pos.update(pos_extension)
    return G, pos


def extend_embedding(
    G_new: nx.Graph, _PG: nx.PlanarEmbedding, pos: VertexPositions
) -> nx.PlanarEmbedding:
    PG = deepcopy(_PG)
    G_diff = nx.Graph(set(G_new.edges).difference(PG.edges))
    edge_list_diff = transform_graph_egdes(G_diff)
    G_join = nx.Graph(set(G_new.edges).union(PG.edges))
    edge_list_all = transform_graph_egdes(G_join)
    for e in edge_list_diff.edges:
        _ = handle_half_edge(PG, pos, edge_list_all, e)
    soft_check_structure(PG)

    return PG


def add_other_vertices(
    G: nx.Graph, PG: nx.PlanarEmbedding, pos: VertexPositions, axis: Axis = "y"
):
    assn = assignments[axis]
    G1, pos1 = create_bounding_ellipse(G, pos)
    outer_edges = [
        (assn.source, assn.other_source),
        (assn.source, assn.other_target),
        (assn.other_source, assn.target),
        (assn.other_target, assn.target),
    ]

    G1.add_edges_from(outer_edges)
    PG1 = extend_embedding(G1, PG, pos1)
    return G1, PG1, pos1, outer_edges


def embed_target_source_edge(_PG: nx.PlanarEmbedding, axis: Axis = "y"):
    # TODO - cleaner logic - can't "extend embedding, bc angles are not appropriate.. "
    assn = assignments[axis]
    PG = deepcopy(_PG)

    if axis == "y":
        PG.add_half_edge_ccw(
            assn.source, assn.target, reference_neighbor=assn.other_source
        )
    else:
        PG.add_half_edge_cw(
            assn.source, assn.target, reference_neighbor=assn.other_source
        )
    source_nbs = list(PG.neighbors_cw_order(assn.source))
    assert source_nbs[0] == assn.target or source_nbs[-1] == assn.target

    if axis == "y":
        PG.add_half_edge_cw(
            assn.target, assn.source, reference_neighbor=assn.other_source
        )
    else:
        PG.add_half_edge_ccw(
            assn.target, assn.source, reference_neighbor=assn.other_source
        )
    target_nbs = list(PG.neighbors_cw_order(assn.target))
    assert target_nbs[0] == assn.source or target_nbs[-1] == assn.source

    directed_edges = [(assn.source, assn.target)]
    soft_check_structure(PG)
    return PG, directed_edges


# TODO this is in a very specific instance.. where have source target graphs.. 
def fully_embed_graph(G: nx.Graph, pos: VertexPositions, axis: Axis):
    directed_edges = list(G.edges)
    PG = create_embedding(G, pos)

    _, PG1, pos1, new_edges1 = add_other_vertices(G, PG, pos, axis)

    PG2, new_edges2 = embed_target_source_edge(PG1, axis)
    return EmbedResult(PG2, pos1, sorted(directed_edges + new_edges1 + new_edges2))
