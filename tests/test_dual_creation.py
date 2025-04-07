import networkx as nx
import pytest

from graph2plan.dual.check import (
    check_correct_n_faces_in_edge_face_dict,
    check_is_source_target_graph,
)
from graph2plan.dual.create_dual import create_dual, prep_dual
from graph2plan.dual.create_rectangle import (
    calculate_x_domains,
)
from graph2plan.dual.examples import fully_embed_kant
from graph2plan.external_embed.main import EmbedResult


@pytest.mark.parametrize(
    "ix", [0, 1]
)
def test_valid_embedding(ix):
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    PG.check_structure()
    assert len(PG.edges) / 2 == len(directed_edges)
    directed_planar_graph = nx.DiGraph(PG.to_directed().edge_subgraph(directed_edges))
    check_is_source_target_graph(directed_planar_graph)
    assert PG.order() == len(pos)

@pytest.mark.parametrize(
    "ix", [0, 1]
)
def test_dual_preparation(ix):
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    edge_face_dict = prep_dual(PG, directed_edges)
    assert len(PG.edges) / 2 == len(edge_face_dict)
    check_correct_n_faces_in_edge_face_dict(edge_face_dict)
    #

@pytest.mark.parametrize(
    "ix", [0, 1]
)
def test_dual_creation(ix):
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    edge_face_dict = prep_dual(PG, directed_edges)
    dual_graph, dual_pos = create_dual(edge_face_dict, pos)
    check_is_source_target_graph(dual_graph)

@pytest.mark.parametrize(
    "ix", [0, 1]
)
def test_calc_x_domains(ix):
    res = fully_embed_kant()
    PG, pos, directed_edges = res[ix]
    edge_face_dict = prep_dual(PG, directed_edges)
    dual_graph, dual_pos = create_dual(edge_face_dict, pos)
    x_domains = calculate_x_domains(dual_graph, PG, directed_edges)
    # number of nodes should be n in original embedding - 2
    assert len(x_domains) == PG.order() - 2
