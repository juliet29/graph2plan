from dataclasses import dataclass
import networkx as nx
from sympy import ordered
from .canonical_interfaces import CanonicalOrder, G_canonical
from copy import deepcopy
from ..helpers.utils import set_intersection
# delete vs, vn..
# direct edges from vi to vj if i  < j
# determine left edge, right edge, + basis edge
# segment t1, t2 and check if have a rel..


@dataclass
class RELVertexData:
    left_edge:  str = ""
    right_edge:  str = ""
    basis_edge:  str = ""
    left_point:  str = ""
    right_point:  str = ""
    # TODO can decide to have more complex data structure.. but cant be tuple because will be updating.. 

def initialize_rel_graph(_G: nx.Graph):
    G = deepcopy(_G)
    new_attributes = {n: RELVertexData() for n in G.nodes}
    nx.set_node_attributes(G, values=new_attributes, name="data")
    
    # nx.Graph[str, dict[str, RELVertexData]]
    # Node
    return G




def find_rel_edges(G: nx.Graph, co: CanonicalOrder, node: str):
    nbs = G.neighbors(node)
    higher_order_nbs = [nb for nb in nbs if co.vertices[nb].ordered_number > co.vertices[node].ordered_number]
    if co.vertices[node].ordered_number < co.n:
        assert len(higher_order_nbs) >= 1, f"No higher ordered nbs for {node}"
    # TODO better way check that will be right type of graph.., ie that nodes have the correct attributes.. 
    assert isinstance(G.nodes[node]["data"], RELVertexData)

    sorted_nbs = sorted(higher_order_nbs, key=lambda x: co.vertices[x].ordered_number)

    if sorted_nbs:
        G.nodes[node]["data"].left_edge = sorted_nbs[0] #min(higher_order_nbs) # TODO check this is accurate!
        G.nodes[node]["data"].right_edge = sorted_nbs[-1] #max(higher_order_nbs)

    return G


def find_basis_edge(G: nx.Graph, co: CanonicalOrder, node: str):
    nbs = G.neighbors(node)
    lower_ordered_nbs = [nb for nb in nbs if co.vertices[nb].ordered_number < co.vertices[node].ordered_number]
    if co.vertices[node].ordered_number > 1:
        assert len(lower_ordered_nbs) >= 1, f"No lowered ordered nbs for {node}"
    # TODO better way check that will be right type of graph.., ie that nodes have the correct attributes.. 
    assert isinstance(G.nodes[node]["data"], RELVertexData)
    sorted_nbs = sorted(lower_ordered_nbs, key=lambda x: co.vertices[x].ordered_number)

    if sorted_nbs:
        G.nodes[node]["data"].basis_edge = sorted_nbs[0]

    return G


def find_rel_points(G_c: G_canonical, G:nx.Graph,  co: CanonicalOrder, node: str):
    cw_nbs = G_c.embedding.neighbors_cw_order(node)

    k = co.vertices[node].ordered_number
    outer_face = G_c.outer_face_at_k_minus_1(co, k) # TODO check this.. 
    overlap = [i for i in cw_nbs if i in outer_face]

    if len(overlap) >= 2:
        G.nodes[node]["data"].left_point = overlap[-1]
        G.nodes[node]["data"].right_point = overlap[0]


    return G

def create_rel(G_c: G_canonical, co: CanonicalOrder):
    Ginit = initialize_rel_graph(G_c.G)
    for node in Ginit.nodes:
        Ginit = find_rel_edges(Ginit, co, node)
        Ginit = find_basis_edge(Ginit, co, node)
        Ginit = find_rel_points(G_c, Ginit, co, node)

    return Ginit






















