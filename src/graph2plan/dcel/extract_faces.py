import networkx as nx

def check_num_faces_is_correct(num_nodes, num_half_edges, num_faces):
    # print(f"num_faces: {num_faces}")
    num_edges = num_half_edges // 2 
    expected_faces = num_edges - num_nodes + 2
    try:
        assert num_nodes - num_edges + num_faces == 2
    except AssertionError:
        print(f"Error! nodes {num_nodes}, edges {num_edges} | faces={num_faces} != exp_faces={expected_faces}")
def extract_faces(PG: nx.PlanarEmbedding):
    """[Based on networkx source code](https://networkx.org/documentation/stable/_modules/networkx/algorithms/planarity.html#PlanarEmbedding.check_structure)"""

    num_nodes = len(PG.nodes)
    counted_half_edges = set()
    num_faces = 0
    num_half_edges = 0
    faces = {}
    for v in PG.nodes:
        for w in PG.neighbors_cw_order(v):
            num_half_edges += 1
            if (v, w) not in counted_half_edges:
                # We encountered a new face
                num_faces += 1
                # Mark all half-edges belonging to this face
                face = PG.traverse_face(v, w, counted_half_edges)
                faces[num_faces] = face
                # print(f"==>> face: {face}")
    check_num_faces_is_correct(num_nodes, num_half_edges, num_faces)
    return faces

# TODO check out using e.next_face_half_edge.. 
# def extract_faces(PG: nx.PlanarEmbedding):


