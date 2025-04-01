import networkx as nx
from graph2plan.dual.check import (
    check_correct_n_faces_in_edge_face_dict,
    check_is_source_target_graph,
)
from graph2plan.dual.examples import embedded_kant_G1
from graph2plan.dcel.extract_faces import (
    prep_dual,
    create_dual,
    calculate_x_domains,
    find_vertex_faces,
    get_node_by_face,
)
from graph2plan.dual.interfaces import DualVertex


def test_valid_embedding():
    PG, pos, directed_edges = embedded_kant_G1()
    PG.check_structure()
    assert len(PG.edges) / 2 == len(directed_edges)
    directed_planar_graph = nx.DiGraph(PG.to_directed().edge_subgraph(directed_edges))
    check_is_source_target_graph(directed_planar_graph)
    assert PG.order() == len(pos)


def test_dual_preparation():
    PG, pos, directed_edges = embedded_kant_G1()
    edge_face_dict = prep_dual(PG, directed_edges)
    assert len(PG.edges) / 2 == len(edge_face_dict)
    check_correct_n_faces_in_edge_face_dict(edge_face_dict)
    #


def test_dual_creation():
    PG, pos, directed_edges = embedded_kant_G1()
    edge_face_dict = prep_dual(PG, directed_edges)
    dual_graph, dual_pos = create_dual(edge_face_dict, pos)
    check_is_source_target_graph(dual_graph)


def test_calc_x_domains():
    PG, pos, directed_edges = embedded_kant_G1()
    edge_face_dict = prep_dual(PG, directed_edges)
    dual_graph, dual_pos = create_dual(edge_face_dict, pos)
    x_domains = calculate_x_domains(dual_graph, PG, directed_edges)
    # number of nodes should be n in original embedding - 2
    assert len(x_domains) == PG.order() - 2
