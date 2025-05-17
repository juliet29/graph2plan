from dataclasses import dataclass
import functools
import networkx as nx
from shapely import symmetric_difference
from sympy import ordered

from graph2plan.helpers.geometry_interfaces import VertexPositions
from .canonical_interfaces import CanonicalOrder, G_canonical
from copy import deepcopy
from ..helpers.utils import set_difference, set_intersection
from ..helpers.graph_interfaces import cardinal_directions, get_exterior_names
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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

    # if len(overlap) >= 2:
    #     G.nodes[node]["data"].left_point = overlap[-1]
    #     G.nodes[node]["data"].right_point = overlap[0]

    ordered_overlap = sorted([(i, co.vertices[i].ordered_number) for i in overlap], key=lambda j: j[1])

    if len(overlap) >= 2:
        G.nodes[node]["data"].left_point = ordered_overlap[0][0]
        G.nodes[node]["data"].right_point = ordered_overlap[-1][0]


    return G

@functools.lru_cache
def create_rel(G_c: G_canonical, co: CanonicalOrder):
    Ginit = initialize_rel_graph(G_c.G)
    Ginit.remove_edge(u="v_n", v="v_s")

    for node in Ginit.nodes:
        Ginit = find_rel_edges(Ginit, co, node)
        Ginit = find_basis_edge(Ginit, co, node)
        Ginit = find_rel_points(G_c, Ginit, co, node)

    return Ginit

def extract_graphs(Ginit:nx.Graph):
    T1 = nx.DiGraph()
    T2 = nx.DiGraph()
    exterior_names = get_exterior_names()
    default_graph = T2


    for node, data in Ginit.nodes(data=True):
        res:RELVertexData = data["data"]
        if node not in exterior_names:
            T1.add_edge(node, res.left_edge)
            T2.add_edge(node, res.right_edge)

            if res.basis_edge == res.right_point:
                T1.add_edge(res.basis_edge, node, basis=True)
            elif res.basis_edge == res.left_point:
                T2.add_edge(res.basis_edge, node, basis=True)
            else:
                default_graph.add_edge(res.basis_edge, node, basis=True)

    # T1.remove_nodes_from(exterior_names)
    # T2.remove_nodes_from(exterior_names)

    # for node in exterior_names:
    #     nbs = Ginit.neighbors(node)
    #     interior_nbs = set_difference(nbs, exterior_names)
    #     for nb in interior_nbs:
    #         match node:
    #             case "v_n":
    #                 T1.add_edge(nb, node)
    #             case "v_s":
    #                 T1.add_edge(node, nb)
    #             case "v_e":
    #                 T2.add_edge(nb, node)
    #             case "v_w":
    #                 T2.add_edge(node, nb)



    return T1, T2






def plot_rel(Ginit:nx.Graph, T1:nx.DiGraph, T2:nx.DiGraph, pos:VertexPositions, co: CanonicalOrder):
    fig, ax = plt.subplots()

    nx.draw_networkx_nodes(Ginit, pos, ax=ax, node_size=400, node_shape="s")
    nx.draw_networkx_labels(Ginit, pos, ax=ax, labels={n:f"{co.vertices[n].ordered_number}\n({n})" for n in Ginit.nodes}, font_size=8)

    # def meta_filter_edge(G, val, n1, n2):
    #     return G[n1][n2].get("basis", val)
    
    # T1_non_basis_edges = 


    nx.draw_networkx_edges(T1, pos, edge_color="blue", ax=ax, label="T1")
    nx.draw_networkx_edges(T2, pos, edge_color="red", ax=ax, label="T2")
    nx.draw_networkx_edge_labels(T1, pos, edge_labels={(u,v): data["basis"] for u,v,data in T1.edges(data=True) if data})

    nx.draw_networkx_edge_labels(T2, pos, edge_labels={(u,v): data["basis"] for u,v,data in T2.edges(data=True) if data})

    legend_elements = [
        Line2D([0], [0], color='blue', lw=2, label='T1'),
        Line2D([0], [0], color='red', lw=2, label='T2'),
    ]
    
    # Add the legend to the plot
    plt.legend(handles=legend_elements, title="Edge Types")
    # plt.legend()

    plt.show()


























