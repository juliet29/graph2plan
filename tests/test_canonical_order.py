import pytest

from graph2plan.canonical.canonical_order import (
    create_canonical_order,
    initialize_canonical_order
)
from graph2plan.main.examples import kk85_outer_face
from graph2plan.fourtp.four_complete import four_complete
from graph2plan.main.tests import kk85


@pytest.fixture()
def canonical_ordering_kk85():
    G, pos = kk85()
    G, full_pos = four_complete(G, pos, kk85_outer_face())
    G_c, co= create_canonical_order(G, pos, full_pos)
    return G_c, co


def test_canonical_order_kk85(canonical_ordering_kk85):
    G_c, co = canonical_ordering_kk85
    assert G_c
    assert co


def test_canonical_order_kk85_is_ordered(saved_co_kk85):
    _, co_vertices, _ = saved_co_kk85
    for i in co_vertices.values():
        assert i > 0


def test_hashing_co():
    G, pos = kk85()
    G, full_pos = four_complete(G, pos, kk85_outer_face())
    G_c, co = initialize_canonical_order(G, pos, full_pos)
    G_c1, co1 = initialize_canonical_order(G, pos, full_pos)
    assert G_c == G_c1
    assert co == co1
    assert co.__hash__() == co1.__hash__()
    assert G_c1.__hash__() == G_c.__hash__()


# TODO more complex tests, like checking the definitions of a canon order is satisfied.. -> can make faster by pulling out the tests..
