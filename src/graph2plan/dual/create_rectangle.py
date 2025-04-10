import networkx as nx
from itertools import cycle
from functools import partial

from graph2plan.helpers.general_interfaces import (
    Axis,
    Face,
    get_assignments,
    get_node_alias,
)
from graph2plan.dual.create_dual import get_node_by_face
from graph2plan.dual.interfaces import MarkedNb, VertexDomain
from graph2plan.helpers.utils import pairwise


def find_vertex_faces(PG: nx.PlanarEmbedding, directed_edges: list[tuple], node):
    dpg = PG.to_directed().edge_subgraph(directed_edges)
    cw_neighbors = list(PG.neighbors_cw_order(node))
    incoming = list(dpg.predecessors(node))  # type: ignore
    outgoing = list(dpg.successors(node))  # type: ignore

    marked_cw_nbs = []
    for nb in cw_neighbors:
        if nb in incoming:
            marked_cw_nbs.append(MarkedNb(nb, "IN"))
        elif nb in outgoing:
            marked_cw_nbs.append(MarkedNb(nb, "OUT"))
        else:
            raise Exception("should be in incoming or outgoing")
    # print(f"==>> marked_cw_nbs: {marked_cw_nbs}")

    nb_cycle = cycle(marked_cw_nbs)
    count = 0

    incoming_face_edge, outgoing_face_edge = None, None
    left_face, right_face = None, None

    for a, b in pairwise(nb_cycle):
        # print(f"==>> a,b: {a,b}")
        count += 1
        if not incoming_face_edge and a.mark == "IN" and b.mark == "OUT":
            incoming_face_edge = sorted([a, b], key=lambda x: x.mark)
            continue

        if not outgoing_face_edge and a.mark == "OUT" and b.mark == "IN":
            outgoing_face_edge = sorted([a, b], key=lambda x: x.mark)
            continue

        if incoming_face_edge and outgoing_face_edge:
            left_face = Face(PG.traverse_face(node, incoming_face_edge[0].name))
            right_face = Face(PG.traverse_face(outgoing_face_edge[0].name, node))
            break

        if count > len(marked_cw_nbs) * 2:
            raise Exception(
                f"Can't find incoming and outgoing for {node} -> {incoming}, {outgoing}"
            )

    assert left_face and right_face
    return left_face, right_face


def get_longest_path_length(G, source, target):
    # print(list(nx.all_simple_paths(G, source, target)))
    path_lengths = [len(x) for x in nx.all_simple_paths(G, source, target)]
    # print(path_lengths)

    sorted_paths = sorted(path_lengths, reverse=True)
    return sorted_paths[0]-1


def calculate_x_domains(
    dual_graph: nx.DiGraph, PG: nx.PlanarEmbedding, directed_edges: list[tuple]
):
    source = "w*"
    target = "e*"
    d1 = partial(get_longest_path_length, dual_graph, source)
    D1 = d1(target)
    print(f"==>> D1: {D1}")

    vertex_distances: dict[str, VertexDomain] = {}

    for node in PG.nodes:
        if node == "v_s" or node == "v_n":
            continue
        left_face, right_face = find_vertex_faces(PG, directed_edges, node)
        v_left = get_node_by_face(dual_graph, left_face)
        v_right = get_node_by_face(dual_graph, right_face)
        vertex_distances[node] = VertexDomain(d1(v_left), d1(v_right))
    print(f"==>> vertex_distances: {vertex_distances}")

    return vertex_distances


def calculate_domains(
    dual_graph: nx.DiGraph,
    PG: nx.PlanarEmbedding,
    directed_edges: list[tuple],
    axis: Axis,
):
    assn = get_assignments(axis)
    source, target = (
        get_node_alias(assn.other_source),
        get_node_alias(assn.other_target),
    )
    print(f"==>> source: {assn.source}")
    print(f"==>> target: {assn.target}")

    d1 = partial(get_longest_path_length, dual_graph, source)
    D1 = d1(target)
    print(f"==>> D1: {D1}")

    vertex_distances: dict[str, VertexDomain] = {}

    for node in PG.nodes:
        if node == assn.source or node == assn.target:
            continue
        elif node == assn.other_source or node == assn.other_target:
            continue

        left_face, right_face = find_vertex_faces(PG, directed_edges, node)
        v_left = get_node_by_face(dual_graph, left_face)
        v_right = get_node_by_face(dual_graph, right_face)
        v_domain = VertexDomain(d1(v_left), d1(v_right)) if axis == "y" else  VertexDomain(d1(v_right), d1(v_left))
        vertex_distances[node] = v_domain


    if axis == "y":
        vertex_distances[assn.source] = VertexDomain(1, D1 - 1)
        vertex_distances[assn.target] = VertexDomain(1, D1 - 1)
        vertex_distances[assn.other_source] = VertexDomain(0, 1)
        vertex_distances[assn.other_target] = VertexDomain(D1 - 1, D1)
    else:
        vertex_distances[assn.source] = VertexDomain(0, D1)
        vertex_distances[assn.target] = VertexDomain(0, D1)
        vertex_distances[assn.other_source] = VertexDomain(0,1)
        vertex_distances[assn.other_target] = VertexDomain(D1 - 1, D1)


    for key, value in vertex_distances.items():
        try:
            value.check_is_valid()
        except AssertionError as a:
            print(f"{key} has invalid distance: {a}")

    print(f"==>> vertex_distances: {vertex_distances}")

    return vertex_distances



