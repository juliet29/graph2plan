from graph2plan.dcel.extract_faces import EdgeFaceDict
from graph2plan.dcel.interfaces import T


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
