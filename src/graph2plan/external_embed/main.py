from collections import namedtuple
from typing import Literal
from graph2plan.dcel.create import create_embedding, extend_embedding
from graph2plan.dcel.interfaces import transform_graph_egdes
from graph2plan.helpers.general_interfaces import CoordinateList, ShapelyBounds, VertexPositions
from ..dual.examples import kant_G1, kant_G2
import networkx as nx
from shapely import MultiPoint
from copy import deepcopy
from .outer_face import get_outer_face_st_graph, split_outer_face
import matplotlib.pyplot as plt


    

def create_bounding_ellipse(_G:nx.Graph, _pos: VertexPositions):
    pos = deepcopy(_pos)
    G = deepcopy(_G)
    points = MultiPoint([p for p in pos.values()])
    bounds = ShapelyBounds(*points.envelope.bounds)
    new_pos = bounds.circular_cardinal_values()._asdict()
    pos_extension = dict(set(new_pos.items()) - set(pos.items()))
    G.add_nodes_from(pos_extension.keys())
    pos.update(pos_extension)
    return G, pos 

Assignments = namedtuple("Assignments", ["source", "target", "other_source", "other_target"])


assignments = {
    "x": Assignments("v_w", "v_e", "v_s", "v_n"),
    "y": Assignments("v_s", "v_n", "v_w", "v_e",)
}


def add_other_vertices(G:nx.Graph, PG: nx.PlanarEmbedding, pos: VertexPositions, axis: Literal["x", "y"]="x"):
    assn = assignments[axis]
    G1, pos1 =  create_bounding_ellipse(G, pos)
    outer_face = get_outer_face_st_graph(PG, pos, assn.source)
    if axis == "y":
        other_source_nbs, other_target_nbs = split_outer_face(outer_face, assn.source, assn.target)
    elif axis == "x":
        other_target_nbs, other_source_nbs = split_outer_face(outer_face, assn.source, assn.target)

    new_edges = [(assn.other_source, i) for i in other_source_nbs] + [(i, assn.other_target) for i in other_target_nbs]
    G1.add_edges_from(new_edges)
    PG1 = extend_embedding(G1, PG, pos1)
    plt.figure()
    nx.draw_networkx(PG1.to_directed(), pos1)
    return G1, PG1, pos1


    





def test():
    G, pos = kant_G1()
    PG = create_embedding(G, pos)
    G1, PG1, pos1 = add_other_vertices(G, PG, pos, "y")

    return G1, PG1, pos1


def test2():
    G, pos = kant_G2()
    nx.draw_networkx(G, pos)
    PG = create_embedding(G, pos)
    G1, PG1, pos1 = add_other_vertices(G, PG, pos, "x")

    return G1, PG1, pos1

    # # nx.draw_networkx(G, pos)
    # G1, pos1, pts =  create_bounding_ellipse(G, pos)
    # # plt.figure()
    # # nx.draw_networkx(G1, pos1)

    # PG = create_embedding(G, pos)
    # outer_face = get_outer_face_st_graph(PG, pos)
    # other_source_nbs, other_target_nbs = split_outer_face(outer_face)

    # # TODO "extra" edges, connect to either half of face.. 

    # new_edges = [("v_w", i) for i in other_source_nbs] + [(i, "v_e") for i in other_target_nbs]
    # G1.add_edges_from(new_edges)
    # # TODO check angles.. 
    # # G1.remove_nodes_from(["north", "south"])

    # plt.figure()
    # nx.draw_networkx(G1, pos1)



    return G1, pos1, PG
