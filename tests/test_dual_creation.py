import math
import networkx as nx
import pytest

from graph2plan.dual.helpers import (
    check_correct_n_faces_in_edge_face_dict,
    check_is_source_target_graph,
)
from graph2plan.dual.create_dual import create_dual, prep_dual
from graph2plan.dual.create_domains import calculate_domains, merge_domains
from graph2plan.dual.examples import (
    create_domains_for_kant,
    fully_embed_kant,
)


@pytest.mark.parametrize("ix", [0, 1])
def test_valid_embedding(ix):
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    PG.check_structure()
    assert len(PG.edges) / 2 == len(directed_edges)
    directed_planar_graph = nx.DiGraph(PG.to_directed().edge_subgraph(directed_edges))
    check_is_source_target_graph(directed_planar_graph)
    assert PG.order() == len(pos)


@pytest.mark.parametrize("ix", [0, 1])
def test_dual_preparation(ix):
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    edge_face_dict = prep_dual(PG, directed_edges)
    assert len(PG.edges) / 2 == len(edge_face_dict)
    check_correct_n_faces_in_edge_face_dict(edge_face_dict)
    #


@pytest.mark.parametrize("ix", [0, 1])
def test_dual_creation(ix):
    axis = "y" if ix == 0 else "x"
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    edge_face_dict = prep_dual(PG, directed_edges)
    dual_graph, dual_pos = create_dual(edge_face_dict, pos, axis)
    check_is_source_target_graph(dual_graph)


@pytest.mark.parametrize("ix", [0, 1])
def test_calc_domains(ix):
    axis = "y" if ix == 0 else "x"
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    edge_face_dict = prep_dual(PG, directed_edges)
    dual_graph, dual_pos = create_dual(edge_face_dict, pos, axis)

    domains = calculate_domains(dual_graph, PG, directed_edges, axis)
    assert len(domains) == PG.order()


@pytest.fixture()
def doms():
    x_domains, y_domains = create_domains_for_kant()
    doms = merge_domains(x_domains, y_domains)
    return doms


def test_merged_domains_are_rectangular(doms):
    union = doms.to_shapely_rectangles()
    assert math.isclose(union.minimum_rotated_rectangle.area, union.area)


def test_opposite_external_rectangles_have_equal_area(doms):
    def get_area(name):
        [name] = [i for i in doms.domains if i.name == name]
        return name.bounds.to_shapely_rectangle().area

    assert get_area("v_s") == get_area("v_n")
    assert get_area("v_e") == get_area("v_w")
