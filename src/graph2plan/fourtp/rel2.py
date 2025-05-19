from copy import deepcopy
from dataclasses import dataclass

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from graph2plan.dual.helpers import check_is_source_target_graph
from graph2plan.fourtp.canonical_interfaces import CanonicalOrder
from graph2plan.helpers.geometry_interfaces import VertexPositions

from matplotlib.axes import Axes

from graph2plan.helpers.utils import pairwise, set_intersection
from .canonical_interfaces import CanonicalOrder, G_canonical

import networkx as nx
from itertools import cycle


@dataclass
class RELVertexData:
    left_edge: str = ""
    right_edge: str = ""
    basis_edge: str = ""
    left_point: str = ""
    right_point: str = ""
    # TODO can decide to have more complex data structure.. but cant be tuple because will be updating..

    def show_co(self, co: CanonicalOrder, node: str):
        curr = co.vertices[node].ordered_number
        le = co.vertices[self.left_edge].ordered_number
        re = co.vertices[self.right_edge].ordered_number
        b = co.vertices[self.basis_edge].ordered_number
        lp = co.vertices[self.left_point].ordered_number
        rp = co.vertices[self.right_point].ordered_number
        # r = f"curr: {curr}. basis: {b} \nedges: ({le}, {re}). points: ({lp, rp}). "
        r2 = f"node: {curr} | rp, re: {rp}->{re} | le, lp: {le}->{lp}"
        # print(r)
        print(r2)


def initialize_rel_graph(_G: nx.Graph, co: CanonicalOrder):
    G = nx.DiGraph()

    for u, v in _G.edges:
        if u == "v_n" and v == "v_s":
            continue
        elif v == "v_n" and u == "v_s":
            continue
        order_u = co.vertices[u].ordered_number
        order_v = co.vertices[v].ordered_number
        if order_u < order_v:
            G.add_edge(u, v)
        elif order_u > order_v:
            G.add_edge(v, u)
        else:
            raise Exception(f"{u}-{order_u} and {v}-{order_v} have the same order!")

    new_attributes = {n: RELVertexData() for n in G.nodes}
    nx.set_node_attributes(G, values=new_attributes, name="data")

    return G


# find nbs in cw order -> need embedding
# create a cycle.. + demarate incoming and outgoing edges
# find in,out and out,in..
# but dont have to recompute each time..
# can also asign the basis edge at this point.. -> just find incoming edge that is the least..
def assign_rel_values_for_node(
    G: nx.DiGraph, embedding: nx.PlanarEmbedding, co: CanonicalOrder, node: str
):
    cw_nbs = list(embedding.neighbors_cw_order(node))[::-1]
    count = 0
    nb_cycle = cycle(cw_nbs)
    incoming = list(G.predecessors(node))  # type: ignore
    outgoing = list(G.successors(node))  # type: ignore

    data: RELVertexData = G.nodes[node]["data"]

    data.basis_edge = sorted(
        set_intersection(cw_nbs, incoming), key=lambda x: co.vertices[x].ordered_number
    )[0]

    right, left = False, False

    for a, b in pairwise(nb_cycle):
        count += 1
        if a in incoming and b in outgoing:
            data.right_point = a
            data.right_edge = b
            # print(f"in, out: {co.vertices[a].ordered_number,co.vertices[b].ordered_number}")

            right = True
        if a in outgoing and b in incoming:
            data.left_edge = a
            data.left_point = b
            left = True
            # print(f"out, in: {co.vertices[a].ordered_number,co.vertices[b].ordered_number}")

        if right and left:
            data.show_co(co, node)
            break

        if count > len(cw_nbs) * 2:
            raise Exception(
                f"Can't find incoming and outgoing for {node} -> {incoming}, {outgoing}"
            )
        # TODO think about exceptions..  some will have no incoming and outgoing..

    return G


def create_rel(_G: nx.Graph, co: CanonicalOrder, embedding: nx.PlanarEmbedding):
    Ginit = initialize_rel_graph(_G, co)
    for node in Ginit.nodes:
        if node in ["v_n", "v_s", "v_w", "v_e"]:  # TODO better way for this..
            continue
        Ginit = assign_rel_values_for_node(Ginit, embedding, co, node)

    return Ginit

def assign_missing_edges(_G:nx.DiGraph, T1: nx.DiGraph, T2: nx.DiGraph):
    G = deepcopy(_G)
    G.remove_edge(u="v_s", v="v_e")
    G.remove_edge(u="v_s", v="v_w")
    G.remove_edge(u="v_e", v="v_n")
    G.remove_edge(u="v_w", v="v_n")
    # TODO this assumes that the REL only applies to interior nodes, but further testing will determine if this is wrong.. 
    # find nodes not in T1 or in T2
    Gdiff = nx.difference(G, nx.compose(T1, T2))
    if not Gdiff.edges:
        print("No missing edges")
        return T1, T2
    
    for u,v in Gdiff.edges:
        assert u in ["v_s", "v_w"] or v in ["v_n", "v_e"], f"Invalid missing edges! {Gdiff.edges}"
        match u:
            case "v_s":
                T1.add_edge(u, v)
                continue
            case "v_w":
                T2.add_edge(u, v)
                continue
            case _:
                pass
        print(f"couldnt match u {u}, so trying to match v {v}")
        match v:
            case "v_n":
                T1.add_edge(u, v)
                continue
            case "v_e":
                T2.add_edge(u, v)
                continue
            case _:
                pass
        
    return T1, T2

    # for outer_node in ["v_s", "v_w","v_n", "v_e"]




def extract_graphs(Ginit: nx.DiGraph):
    T1 = nx.DiGraph()
    T2 = nx.DiGraph()
    # exterior_names = get_exterior_names()
    default_graph = T1

    for node, data in Ginit.nodes(data=True):
        res: RELVertexData = data["data"]
        # if node not in exterior_names:

        if res.left_edge and res.right_edge:
            T1.add_edge(node, res.left_edge)
            T2.add_edge(node, res.right_edge)

        if res.basis_edge:
            if res.basis_edge == res.right_point:
                T1.add_edge(res.basis_edge, node, basis=True)
            elif res.basis_edge == res.left_point:
                T2.add_edge(res.basis_edge, node, basis=True)
            else:
                default_graph.add_edge(res.basis_edge, node, basis=True)
    T1, T2 = assign_missing_edges(Ginit, T1, T2)

    return T1, T2




def plot_ordered_nodes(G: nx.Graph, pos: VertexPositions, co: CanonicalOrder, ax: Axes):
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=400, node_shape="s")
    nx.draw_networkx_labels(
        G,
        pos,
        ax=ax,
        labels={n: f"{co.vertices[n].ordered_number}\n({n})" for n in G.nodes},
        font_size=8,
    )
    return ax


def plot_rel_edges(T1: nx.DiGraph, T2: nx.DiGraph, pos: VertexPositions, ax: Axes):
    nx.draw_networkx_edges(T1, pos, edge_color="blue", ax=ax, label="T1")
    nx.draw_networkx_edges(T2, pos, edge_color="red", ax=ax, label="T2")
    nx.draw_networkx_edge_labels(
        T1,
        pos,
        edge_labels={
            (u, v): data["basis"] for u, v, data in T1.edges(data=True) if data
        },
    )

    nx.draw_networkx_edge_labels(
        T2,
        pos,
        edge_labels={
            (u, v): data["basis"] for u, v, data in T2.edges(data=True) if data
        },
    )

    legend_elements = [
        Line2D([0], [0], color="blue", lw=2, label="T1"),
        Line2D([0], [0], color="red", lw=2, label="T2"),
    ]

    # Add the legend to the plot
    plt.legend(handles=legend_elements, title="Edge Types")


def plot_rel_base_graph(G: nx.DiGraph, pos: VertexPositions, co: CanonicalOrder, st_graphs=None):
    fig, ax = plt.subplots()
    plot_ordered_nodes(G, pos, co, ax)
    if st_graphs:
        T1, T2 = st_graphs
        plot_rel_edges(T1, T2, pos, ax)
    else:
        nx.draw_networkx_edges(G, pos)

    plt.show()
