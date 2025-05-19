from ast import excepthandler

import networkx as nx

from graph2plan.dcel.original import create_embedding

from ..dual.helpers import get_embedding_faces


# TODO have different classes - based on first level, triangulation, four-connection..
class ImproperGraphError(Exception):
    pass


class Improper3TPGraphError(Exception):
    pass


class Improper4TPGraphError(Exception):
    pass


def check_is_planar(G):
    try:
        assert nx.check_planarity(G)
    except AssertionError:
        raise ImproperGraphError("Four completed graph is not planar")


def check_is_biconnected(G):
    artic_points = len(list(nx.articulation_points(G)))
    try:
        assert artic_points == 0
    except AssertionError:
        raise ImproperGraphError(
            f"not biconnected - articulation points =  {artic_points} "
        )
    # TODO think about if need expelicit 2-connected check..


def check_is_k_connected(G, k):
    assert k == 3 or k == 4
    degrees = list(nx.degree(G))
    for deg in degrees:
        if deg[1] < k:
            if k == 4:
                raise Improper4TPGraphError(
                    f"There exists a node with less than 4 neighbors: {deg}"
                )
            elif k == 3:
                raise Improper3TPGraphError(
                    f"There exists a node with less than 3 neighbors: {deg}"
                )


# def check_is_3_connected(G):
#     check_is_k_connected(G, 3)


def check_is_triangulated_chordal(G):
    assert nx.is_chordal(G), "Graph is not chordal"


def check_interior_faces_are_triangles(PG: nx.PlanarEmbedding):
    faces = get_embedding_faces(PG)
    non_triangular_faces = set()
    for face in faces:
        if face.n_vertices != 3:
            non_triangular_faces.add(face)
        if len(non_triangular_faces) > 1:
            raise Improper3TPGraphError(
                f"At least 2 non-triangular faces: {non_triangular_faces}"
            )


def check_has_no_seperating_triangle(G):
    l3_cycles = sorted(nx.simple_cycles(G, 3))
    m = len(list(G.edges))
    n = len(list(G.nodes))

    if len(l3_cycles) == m - n + 1:
        return
    else:
        raise Improper3TPGraphError(
            f"There are seperating triangles \n {len(l3_cycles)} three cycles ?= {m - n + 1}, where m={m}, n={n}"
        )


def check_is_valid_triangulated(G, pos=None, PG=None):
    check_is_planar(G)
    check_is_biconnected(G)
    # check_is_3_connected(G) # TODO think chordal is better..
    try:
        check_is_triangulated_chordal(G)
    except AssertionError:
        print("Not chordal..checking if interior faces are triangles..")
        if not PG:
            assert pos
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
