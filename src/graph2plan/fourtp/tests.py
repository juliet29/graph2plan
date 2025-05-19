# from .rel import CanonicalOrder, extract_graphs, create_rel
import pickle
from copy import deepcopy

from graph2plan.canonical.canonical_interfaces import (
    CanonicalOrder,
    G_canonical,
    read_canonical_outputs,
)
from graph2plan.dcel.external import fully_embed_graph
from graph2plan.dual.create_domains import merge_domains
from graph2plan.dual.create_rectangle import create_dual_and_calculate_domains
from graph2plan.dual.helpers import check_is_source_target_graph, get_embedding_faces

from ..canonical.canonical_order import (
    initialize_canonical_order,
    iterate_canonical_order,
)
from ..constants import BASE_PATH
from ..rel.rel2 import (
    create_rel,
    extract_graphs,
    initialize_rel_graph,
    plot_rel_base_graph,
)
from .draw_four_complete import draw_four_complete_graph
from .examples import kk85, kk85_outer_face
from .faces import get_embedding_of_four_complete_G, get_external_face
from .four_complete import (
    four_complete,
    place_cardinal,
)


def test_four_complete():
    G, pos = kk85()
    G, path_pairs = four_complete(G, pos, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)

    draw_four_complete_graph(G, pos, full_pos)

    return G, pos, full_pos


def test_co():
    G, pos = kk85()
    G, path_pairs = four_complete(G, pos, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)
    G_c, co = initialize_canonical_order(G, pos, full_pos)
    print("-----Initialization complete---")

    G_c, co = iterate_canonical_order(G_c, co)
    return G_c, co


def pickle_co():
    G_c, co = test_co()
    with open(BASE_PATH / "pickles/co.pickle", "wb") as handle:
        pickle.dump([G_c, co], handle, protocol=pickle.HIGHEST_PROTOCOL)


def show_co():
    with open(BASE_PATH / "pickles/co.pickle", "rb") as handle:
        r1, r2 = pickle.load(handle)
    G_c: G_canonical = r1
    co: CanonicalOrder = r2
    G_c.G.remove_edge(u="v_n", v="v_s")
    G_c.draw_co(co)
    # plot_canonical_order(G_c.G, G_c.full_pos, co)


def setup_rel():
    G_c, co_vertices, pos = read_canonical_outputs()

    # Ginit = initialize_rel_graph(G_c.G, co)
    return G_c, co_vertices, pos


def test_init_rel():
    # G_c, co = test_co()
    # with open(BASE_PATH / "pickles/co.pickle", "rb") as handle:
    #     r1, r2 = pickle.load(handle)
    # G_c: G_canonical = r1
    # co: CanonicalOrder = r2
    G_c, co_vertices, pos = setup_rel()

    Ginit = initialize_rel_graph(G_c, co_vertices)
    plot_rel_base_graph(Ginit, pos, co_vertices)
    return Ginit


def test_assign_rel():
    G_c, co_vertices, pos = setup_rel()
    embedding = get_embedding_of_four_complete_G(G_c, pos)
    Grel = create_rel(G_c, co_vertices, embedding)
    T1, T2 = extract_graphs(Grel)
    plot_rel_base_graph(Grel, pos, co_vertices, (T1, T2))
    check_is_source_target_graph(T1)
    check_is_source_target_graph(T2)
    return Grel, T1, T2, pos
    # assign_rel_values_for_node(Ginit, G_c.embedding, co, "v3")


def test_dual_creation():
    Grel, T1, T2, pos = test_assign_rel()
    res1 = fully_embed_graph(T1, pos, "y")
    res2 = fully_embed_graph(T2, pos, "x")
    x_domains = create_dual_and_calculate_domains(res1, "y", True)
    y_domains = create_dual_and_calculate_domains(res2, "x", True)
    # TODO may have errors because of orientation..
    merged_doms = merge_domains(x_domains, y_domains)
    merged_doms.draw()
    #
    return merged_doms


def test_external_face():
    G, pos = kk85()
    G, path_pairs = four_complete(G, pos, kk85_outer_face())
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
