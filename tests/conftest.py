import pytest

from graph2plan.canonical.canonical_interfaces import read_canonical_outputs

@pytest.fixture()
def saved_co_kk85():
    G_c, co_vertices, pos = read_canonical_outputs()
    return G_c, co_vertices, pos