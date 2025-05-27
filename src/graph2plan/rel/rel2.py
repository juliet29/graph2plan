from copy import deepcopy
from dataclasses import dataclass
from itertools import cycle

import networkx as nx

from graph2plan.canonical.canonical_interfaces import CanonicalVertices
from graph2plan.constants import OUTPUTS_PATH
from graph2plan.dual.helpers import check_is_source_target_graph
from graph2plan.helpers.utils import pairwise, set_intersection, write_graph, read_graph
from typing import NamedTuple
import json


class STGraphs(NamedTuple):
    T1: nx.DiGraph
    T2: nx.DiGraph

    def save_rel_graphs(self, output_path=OUTPUTS_PATH):
        write_graph(self.T1, "T1", output_path)
        write_graph(self.T2, "T2", output_path)

        print(f"Saved graphs to {output_path.parent / output_path.name}")

    @classmethod
    def read_rel_graphs(cls, output_path=OUTPUTS_PATH):
        return cls(read_graph("T1", output_path), read_graph("T2", output_path))


@dataclass
class RELVertexData:
    left_edge: str = ""
    right_edge: str = ""
    basis_edge: str = ""
    left_point: str = ""
    right_point: str = ""
    # TODO can decide to have more complex data structure.. but cant be tuple because will be updating..

    def show_co(self, co_vertices: CanonicalVertices, node: str):
        curr = co_vertices[node]
        le = co_vertices[self.left_edge]
        re = co_vertices[self.right_edge]
        b = co_vertices[self.basis_edge]
        lp = co_vertices[self.left_point]
        rp = co_vertices[self.right_point]
        # r = f"curr: {curr}. basis: {b} \nedges: ({le}, {re}). points: ({lp, rp}). "
        r2 = f"node: {curr} | rp, re: {rp}->{re} | le, lp: {le}->{lp}"
        # print(r)
        print(r2)


def initialize_rel_graph(_G: nx.Graph, co_vertices: CanonicalVertices):
    G = nx.DiGraph()

    for u, v in _G.edges:
        if u == "v_n" and v == "v_s":
            continue
        elif v == "v_n" and u == "v_s":
            continue
        order_u = co_vertices[u]
        order_v = co_vertices[v]
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
    G: nx.DiGraph,
    embedding: nx.PlanarEmbedding,
    co_vertices: CanonicalVertices,
    node: str,
):
    cw_nbs = list(embedding.neighbors_cw_order(node))[::-1]
    count = 0
    nb_cycle = cycle(cw_nbs)
    incoming = list(G.predecessors(node))  # type: ignore
    outgoing = list(G.successors(node))  # type: ignore

    data: RELVertexData = G.nodes[node]["data"]

    data.basis_edge = sorted(
        set_intersection(cw_nbs, incoming), key=lambda x: co_vertices[x]
    )[0]

    right, left = False, False

    for a, b in pairwise(nb_cycle):
        count += 1
        if a in incoming and b in outgoing:
            data.right_point = a
            data.right_edge = b
            # print(f"in, out: {co_vertices[a],co_vertices[b]}")

            right = True
        if a in outgoing and b in incoming:
            data.left_edge = a
            data.left_point = b
            left = True
            # print(f"out, in: {co_vertices[a],co_vertices[b]}")

        if right and left:
            data.show_co(co_vertices, node)
            break

        if count > len(cw_nbs) * 2:
            raise Exception(
                f"Can't find incoming and outgoing for {node} -> {incoming}, {outgoing}"
            )
        # TODO think about exceptions..  some will have no incoming and outgoing..

    return G


def create_rel(
    _G: nx.Graph, co_vertices: CanonicalVertices, embedding: nx.PlanarEmbedding
):
    Ginit = initialize_rel_graph(_G, co_vertices)
    for node in Ginit.nodes:
        if node in ["v_n", "v_s", "v_w", "v_e"]:  # TODO better way for this..
            continue
        Ginit = assign_rel_values_for_node(Ginit, embedding, co_vertices, node)

    return Ginit


def assign_missing_edges(_G: nx.DiGraph, T1: nx.DiGraph, T2: nx.DiGraph):
    G = deepcopy(_G)
    G.remove_edge(u="v_s", v="v_e")
    G.remove_edge(u="v_s", v="v_w")
    G.remove_edge(u="v_e", v="v_n")
    G.remove_edge(u="v_w", v="v_n")
    # TODO this assumes that the REL only applies to interior nodes, but further testing will determine if this is wrong..
    # find nodes not in T1 or in T2
    Gdiff = nx.difference(G, nx.compose(T1, T2))
    print(f"edges potentially in rel {G.edges}")
    if not Gdiff.edges:
        print("No missing edges")
        return T1, T2
    print(f"==>> Gdiff.edges: {Gdiff.edges}")

    for u, v in Gdiff.edges:
        assert u in ["v_s", "v_w"] or v in ["v_n", "v_e"], (
            f"Invalid missing edges! {Gdiff.edges}"
        )
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


def create_rel_and_extract_st_graphs(
    G: nx.Graph, co_vertices: CanonicalVertices, embedding: nx.PlanarEmbedding
):
    Grel = create_rel(G, co_vertices, embedding)
    T1, T2 = extract_graphs(Grel)
    check_is_source_target_graph(
        T1
    )  # TODO checks like this should all come from the same place outside the main worker modules..
    check_is_source_target_graph(T2)

    return Grel, T1, T2
