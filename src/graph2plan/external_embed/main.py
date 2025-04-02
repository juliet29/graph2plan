from graph2plan.dcel.create import create_embedding
from graph2plan.helpers.general_interfaces import CoordinateList, ShapelyBounds, VertexPositions
from ..dual.examples import kant_G1, kant_G2
import networkx as nx
from shapely import MultiPoint
from copy import deepcopy
from .outer_face import get_outer_face_st_graph

    

def create_bounding_ellipse(_G:nx.Graph, _pos: VertexPositions):
    pos = deepcopy(_pos)
    G = deepcopy(_G)
    points = MultiPoint([p for p in pos.values()])
    bounds = ShapelyBounds(*points.envelope.bounds)
    pos_extention = bounds.circular_cardinal_values()._asdict()
    G.add_nodes_from(pos_extention.keys())
    pos.update(pos_extention)
    return G, pos, points 



def test():
    G, pos = kant_G1()
    nx.draw_networkx(G, pos)
    G1, pos1, pts =  create_bounding_ellipse(G, pos)
    nx.draw_networkx(G1, pos1)

    PG = create_embedding(G, pos)
    outer_face = get_outer_face_st_graph(PG, pos)
    return G1, pos1, pts, outer_face
