import networkx as nx
from graph2plan.dual.interfaces import EdgeFaceDict
from graph2plan.helpers.general_interfaces import T


from collections import Counter


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


def check_is_correctly_oriented_source_target_graph(
    G: nx.DiGraph, orientation="x", show=False
):
    source, target = check_is_source_target_graph(G, show)
    if orientation == "x":
        assert source == "w*" and target == "e*"
