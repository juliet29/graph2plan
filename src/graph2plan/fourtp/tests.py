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
    G, co = iterate_canonical_order(G_c, co)
    return G, co