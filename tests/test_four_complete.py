import networkx as nx
from graph2plan.dcel.original import create_embedding
from graph2plan.fourtp.examples import kk85, kk85_outer_face
from graph2plan.fourtp.faces import get_external_face
from graph2plan.fourtp.four_complete import Alphas, four_complete, check_for_shortcuts
from graph2plan.helpers.graph_checks import Improper4TPGraphError, check_is_k_connected
import pytest
from graph2plan.helpers.auto_pos import create_G_and_pos


def test_kk85_is_not_four_complete():
    G, pos = kk85()
    check_is_k_connected(G, 3)
    with pytest.raises(Improper4TPGraphError):
        check_is_k_connected(G, 4) 


def test_four_complete_kk85():
    G, pos = kk85()
    G_fc, _ = four_complete(G, pos, kk85_outer_face())
    check_is_k_connected(G_fc, 3)
    check_is_k_connected(G_fc, 4) 

def test_find_shortcuts():
    G, pos = create_G_and_pos(nx.triangular_lattice_graph(2,2), draw=False)
    PE = create_embedding(G, pos)
    outer_face = get_external_face(PE, pos)
    shortcuts= check_for_shortcuts(G, outer_face)
    assert shortcuts == [((1, 0), (0, 1)), ((0, 1), (1, 1)), ((0, 1), (1, 2))]