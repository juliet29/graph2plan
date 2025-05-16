import functools
from copy import deepcopy

import test

from graph2plan.dual.helpers import get_embedding_faces

from .canonical_order import (
    initialize_canonical_order,
    iterate_canonical_order,
)
from .draw_four_complete import draw_four_complete_graph
from .examples import kk85, kk85_outer_face
from .faces import get_external_face
from .four_complete import (
    four_complete,
    place_cardinal,
)
from .canonical_interfaces import G_canonical, CanonicalOrder
from .rel import extract_graphs, find_rel_edges, find_rel_points, initialize_rel_graph, create_rel, plot_rel


def test_four_complete():
    G, pos = kk85()
    G, path_pairs = four_complete(G, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)

    draw_four_complete_graph(G, pos, full_pos)

    return G, pos, full_pos


@functools.lru_cache
def test_co():
    G, pos = kk85()
    G, path_pairs = four_complete(G, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)
    G_c, co = initialize_canonical_order(G, pos, full_pos)
    print("-----Initialization complete---")

    G_c, co = iterate_canonical_order(G_c, co)
    return G_c, co


def test_rel():
    G_c, co = test_co()
    G4 = create_rel(G_c, co)
    T1, T2 = extract_graphs(G4)
    plot_rel(G4, T1, T2, G_c.full_pos, co)
    # G2 = initialize_rel_graph(G_c.G)
    # G3 = find_rel_edges(G2, co, "v1")
    # G4 = find_rel_points(G_c, G2, co, "v1")
    return T1, T2




def test_external_face():
    G, pos = kk85()
    G, path_pairs = four_complete(G, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)
    G_c, co = initialize_canonical_order(G, pos, full_pos)

    faces = get_embedding_faces(G_c.embedding)

    ext_face_0 = get_external_face(G_c.embedding, G_c.full_pos)
    print(f"==>> ext_face_0: {ext_face_0}")

    _embedding = deepcopy(G_c.embedding)

    _embedding.remove_node("v_n")
    ext_face_1 = get_external_face(_embedding, G_c.full_pos)
    print(f"==>> ext_face_1 (rm v_n): {ext_face_1}")

    _embedding.remove_node("v4")
    ext_face_2 = get_external_face(_embedding, G_c.full_pos)
    print(f"==>> ext_face_2 (rm v4): {ext_face_2}")

    """
    # TODO -> write test!
    ==>> ext_face_0: ['v_n', 'v_s', 'v_e']
    ==>> ext_face_1 (rm v_n): ['v_w', 'v_s', 'v_e', 'v6', 'v4', 'v7']
    ==>> ext_face_2 (rm v4): ['v_w', 'v_s', 'v_e', 'v6', 'v3', 'v7']
    """

    # # face_1 = ['v_s', 'v_n', 'v_w']
    # for face in faces:
    #     print(f"{face}, area: {face.get_signed_area(G_c.full_pos)}")

    return G_c, faces
