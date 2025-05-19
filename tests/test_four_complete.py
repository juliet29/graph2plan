import networkx as nx
from graph2plan.fourtp.examples import kk85, kk85_outer_face
from graph2plan.fourtp.four_complete import Alphas, four_complete
from graph2plan.fourtp.checks import Improper4TPGraphError, check_is_k_connected, check_is_valid_triangulated
import pytest


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
