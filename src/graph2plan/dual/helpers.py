from collections import Counter

import networkx as nx

from graph2plan.dual.interfaces import EdgeFaceDict
from graph2plan.helpers.geometry_interfaces import T
from graph2plan.helpers.graph_interfaces import (
    CardinalDirectionEnum as CDE,
    Face,
    get_vertex_name,
)


def check_num_faces_is_correct(num_nodes, num_half_edges, num_faces):
    # print(f"num_faces: {num_faces}")
    num_edges = num_half_edges // 2
    expected_faces = num_edges - num_nodes + 2
    try:
        assert num_nodes - num_edges + num_faces == 2
    except AssertionError:
        print(
            f"Error! nodes {num_nodes}, edges {num_edges} | faces={num_faces} != exp_faces={expected_faces}"
        )


def get_embedding_faces(G: nx.PlanarEmbedding):
    G.check_structure()
    counted_half_edges = set()
    counted_faces: set[Face] = set()
    num_half_edges = 0
    num_faces = 0
    for v in G:
        for w in G.neighbors_cw_order(v):
            num_half_edges += 1
            if (v, w) not in counted_half_edges:
                # We encountered a new face
                num_faces += 1
                # Mark all half-edges belonging to this face
                new_face = G.traverse_face(v, w, counted_half_edges)
                counted_faces.add(Face(new_face))

    check_num_faces_is_correct(G.order(), len(counted_half_edges), len(counted_faces))

    return counted_faces


def check_correct_n_faces_in_edge_face_dict(edge_face_dict: EdgeFaceDict[T]):
    face_cnt = Counter()

    for pair in edge_face_dict.values():
        for face in pair:
            face_cnt[face] += 1

    node_cnt = Counter()

    for pair in edge_face_dict.keys():
        for vertex in pair:
            node_cnt[vertex] += 1

    n_half_edges = len(edge_face_dict) * 2

    check_num_faces_is_correct(len(node_cnt), n_half_edges, len(face_cnt))


def check_is_source_target_graph(G: nx.DiGraph, show=False):
    sources = [x for x in G.nodes() if G.in_degree(x) == 0]
    targets = [x for x in G.nodes() if G.out_degree(x) == 0]
    assert len(sources) == 1 and len(targets) == 1
    # further, check that all nodes are touched o n paths from s to t..
    if show:
        print(f"==>> sources: {sources}")
        print(f"==>> targets: {targets}")
    return sources[0], targets[0]


# TODO -> this should be easier because should add an attribute when adding the cardinal nodes to the graph..
def split_cardinal_and_interior_nodes(G):
    cardinal_names = [get_vertex_name(i) for i in CDE]
    cardinal_nodes = []
    for node in G.nodes():
        if node in cardinal_names:
            cardinal_nodes.append(node)
    interior_edges = set(G.nodes()).difference(set(cardinal_nodes))
    return cardinal_nodes, interior_edges


def split_cardinal_and_interior_edges(G):
    cardinal_names = [get_vertex_name(i) for i in CDE]
    cardinal_edges = []
    for edge in G.edges():
        source, target = edge
        if source in cardinal_names and target in cardinal_names:
            cardinal_edges.append(edge)
    interior_edges = set(G.edges()).difference(set(cardinal_edges))
    return cardinal_edges, interior_edges


# def check_is_correctly_oriented_source_target_graph(
#     G: nx.DiGraph, axis: Axis = "x", show=False
# ):
#     source, target = check_is_source_target_graph(G, show)
#     if axis == "x":
#         assert source == "w*" and target == "e*"
#     if axis == "y":
#         assert source == "s*" and target == "n*"
