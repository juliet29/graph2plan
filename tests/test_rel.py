import pytest

from graph2plan.dcel.external import fully_embed_graph
from graph2plan.dual.create_domains import merge_domains
from graph2plan.dual.create_rectangle import create_dual_and_calculate_domains
from graph2plan.fourtp.rel2 import create_rel, extract_graphs
from graph2plan.fourtp.tests import check_is_source_target_graph


@pytest.fixture()
def create_rel_kk85(saved_co_kk85):
    G_c, co = saved_co_kk85
    Grel = create_rel(G_c.G, co, G_c.embedding)
    T1, T2 = extract_graphs(Grel)
    return T1, T2




def test_kk85_rel_yields_st_graphs(create_rel_kk85):
    T1, T2 = create_rel_kk85
    check_is_source_target_graph(T1)
    check_is_source_target_graph(T2)

def test_kk85_st_graphs_yield_dual(create_rel_kk85, saved_co_kk85):
    T1, T2 = create_rel_kk85
    G_c, _ = saved_co_kk85
    res1 = fully_embed_graph(T1, G_c.full_pos, "y")
    res2 = fully_embed_graph(T2, G_c.full_pos, "x")
    x_domains = create_dual_and_calculate_domains(res1, "y", True)
    y_domains = create_dual_and_calculate_domains(res2, "x", True)
    merged_doms = merge_domains(x_domains, y_domains)
    # TODO some tests on the merged domains -> like adjacent to south in four-completed graph is adjacent in the merged doms.. 
    assert merged_doms

