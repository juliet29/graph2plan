import pytest

from graph2plan.constants import BASE_PATH
from graph2plan.canonical.canonical_interfaces import G_canonical, CanonicalOrder, read_canonical_outputs
import pickle

@pytest.fixture()
def saved_co_kk85():
    G_c, co_vertices, pos = read_canonical_outputs()
    # with open(BASE_PATH / "pickles/co.pickle", "rb") as handle:
    #     r1, r2 = pickle.load(handle)
    # G_c: G_canonical = r1
    # co: CanonicalOrder = r2
    return G_c, co_vertices, pos