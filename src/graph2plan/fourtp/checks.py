from ast import excepthandler
import networkx as nx
import matplotlib.pyplot as plt

from graph2plan.dcel.original import create_embedding
from ..dual.helpers import get_embedding_faces


class Improper4TPGraphError(Exception):
    pass


def check_is_planar(G):
    planar_check, _ = nx.check_planarity(G)
    try:
        assert planar_check
    except AssertionError:
        raise Improper4TPGraphError("Four completed graph is not planar")


def check_is_biconnected(G):
    artic_points = len(list(nx.articulation_points(G)))
    try:
        assert artic_points == 0
    except AssertionError:
        raise Improper4TPGraphError(
            f"not biconnected - articulation points =  {artic_points} "
        )
    # add two connected check,,


# def check_has_shared_neighbour(G, e):
#     """In a triangulated graph, if two nodes form an edge, they should share a third neighbor"""
#     u, v = e
#     for node in G.nodes:
#         if (node, u) in G.edges and (node, v) in G.edges:
#             # once we find the shared nb, return
#             return True
#     return False


# def check_is_three_connected(G):
#     # TODO - replace with three connected check..
#     for e in G.edges:
#         if not check_has_shared_neighbour(G, e):
#             raise NotTriangulatedError()
#     return


def check_is_k_connected(G, k):
    degrees = list(nx.degree(G))
    for deg in degrees:
        if deg[1] < k:
            raise Improper4TPGraphError(f"Node has less than {k} neighbors: {deg}")


# def check_is_3_connected(G):
#     check_is_k_connected(G, 3)


def check_is_triangulated_chordal(G):
    try:
        assert nx.is_chordal(G)
    except AssertionError:
        raise Improper4TPGraphError("Graph is not chordal")


def check_interior_faces_are_triangles(PG: nx.PlanarEmbedding):
    faces = get_embedding_faces(PG)
    non_triangular_faces = set()
    for face in faces:
        if face.n_vertices != 3:
            non_triangular_faces.add(face)
        if len(non_triangular_faces) > 1:
            raise Improper4TPGraphError(
                f"At least 2 non-triangular faces: {non_triangular_faces}"
            )


def check_has_no_seperating_triangle(G):
    l3_cycles = sorted(nx.simple_cycles(G, 3))
    m = len(list(G.edges))
    n = len(list(G.nodes))

    if len(l3_cycles) == m - n + 1:
        return
    else:
        raise Improper4TPGraphError(
            f"There are seperating triangles \n {len(l3_cycles)} three cycles ?= {m - n + 1}, where m={m}, n={n}"
        )


def check_is_valid_triangulated(G, pos, PG=None):
    check_is_planar(G)
    check_is_biconnected(G)
    # check_is_3_connected(G) # TODO think chordal is better..
    try:
        check_is_triangulated_chordal(G)
    except AssertionError:
        print("Not chordal..checking if interior faces are triangles..")
        if not PG:
            PG = create_embedding(G, pos)
        check_interior_faces_are_triangles(PG)
    check_has_no_seperating_triangle(G)


def check_is_4_connected(G):
    check_is_k_connected(G, 4)


def check_is_valid_4_connected(G, pos):
    check_is_valid_triangulated(G, pos)
    # outer face has to have four nodes..
    check_is_4_connected(G)
    assert nx.is_k_edge_connected(G, 4), "Networkx says not 4 connected"


# ---
def draw_node_positioned_graph(G):
    pos = {i: i for i in G.nodes}
    plt.figure()
    nx.draw_networkx(G, pos)
    return G, pos
