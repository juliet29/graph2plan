import pytest

from graph2plan.fourtp.canonical_order import (
    initialize_canonical_order,
    iterate_canonical_order,
)
from graph2plan.fourtp.examples import kk85_outer_face
from graph2plan.fourtp.four_complete import four_complete, place_cardinal
from graph2plan.fourtp.tests import kk85


@pytest.fixture()
def canonical_ordering_kk85():
    G, pos = kk85()
    G, path_pairs = four_complete(G, pos, kk85_outer_face())
    full_pos = place_cardinal(pos, path_pairs)
    G_c, co = initialize_canonical_order(G, pos, full_pos)
    G_c, co = iterate_canonical_order(G_c, co)
    return G_c, co


def test_canonical_order_kk85(canonical_ordering_kk85):
    G_c, co = canonical_ordering_kk85
    assert G_c
    assert co

def test_canonical_order_kk85_is_ordered(saved_co_kk85):
    _, co_vertices, _ = saved_co_kk85
    for i in co_vertices.values():
        assert i > 0



# TODO more complex tests, like checking the definitions of a canon order is satisfied.. -> can make faster by pulling out the tests.. 