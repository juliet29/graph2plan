from graph2plan.fourtp.canonical_order import (
    update_chords,
    initialize_canonical_order,
    iterate_canonical_order,
)
from graph2plan.fourtp.draw_four_complete import draw_four_complete_graph
from graph2plan.fourtp.examples import kk85, kk85_outer_face
from graph2plan.fourtp.four_complete import (
    four_complete,
    place_cardinal,
)
from graph2plan.dual.helpers import get_embedding_faces
from sympy import Point, Polygon



def test_four_complete():
    G, pos = kk85()
    G, path_pairs = four_complete(G, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)

    draw_four_complete_graph(G, pos, full_pos)

    return G, pos, full_pos

def test_co():
    G, pos = kk85()
    G, path_pairs = four_complete(G, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)
    G_c, co = initialize_canonical_order(G, pos, full_pos)
    print("-----Initialization complete---")
    G_c, co = iterate_canonical_order(G_c, co)
    return G_c, co

def test_external_face():
    G, pos = kk85()
    G, path_pairs = four_complete(G, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)
    G_c, co = initialize_canonical_order(G, pos, full_pos)
    faces = get_embedding_faces(G_c.embedding)

    # # face_1 = ['v_s', 'v_n', 'v_w']
    # for face in faces:
    #     print(f"{face}, area: {face.get_signed_area(G_c.full_pos)}")


    return G_c, faces