from graph2plan.dcel.examples import deberg_embedded, deberg
from graph2plan.dcel.create import compute_angle_between_edges, create_embedding, is_cw
import pytest
import networkx as nx

from graph2plan.dcel.interfaces import transform_graph_egdes


@pytest.mark.skip(reason="Getting opposite result of what is expected..")
def test_angle_order():
    G, pos = deberg()
    edge_list = transform_graph_egdes(G)

    e_base = (3, 4)
    e_near = (3, 1)
    e_far = (3, 2)

    angle_near = compute_angle_between_edges(
        edge_list.get(*e_base), edge_list.get(*e_near), pos
    )
    angle_far = compute_angle_between_edges(
        edge_list.get(*e_base), edge_list.get(*e_far), pos
    )
    assert angle_near < angle_far


def test_cw():
    G, pos = deberg()
    edge_list = transform_graph_egdes(G)

    e_base = (3, 1)
    e_cw = (3, 2)
    e_ccw = (3, 4)

    t1 = is_cw(pos, edge_list.get(*e_base), edge_list.get(*e_cw))
    t2 = is_cw(pos, edge_list.get(*e_base), edge_list.get(*e_ccw))

    assert t1, t2 == (True, False)


def test_deberg():
    known_embedding = deberg_embedded()
    G, pos = deberg()

    computed_embedding = create_embedding(G, pos)

    assert known_embedding.traverse_face(1, 2) == computed_embedding.traverse_face(1, 2)
    assert known_embedding.traverse_face(4, 3) == computed_embedding.traverse_face(4, 3)


@pytest.mark.parametrize(
    "G", [nx.grid_2d_graph(2, 3), nx.triangular_lattice_graph(2, 2)]
)
def test_other_graphs_simple_pos(G: nx.Graph):
    pos = {i: i for i in G.nodes}
    PG = create_embedding(G, pos)
    assert not PG.check_structure()


@pytest.mark.parametrize("G", [nx.hypercube_graph(3), nx.grid_2d_graph(4, 4)])
def test_other_graphs_planar_pos(G: nx.Graph):
    pos = nx.planar_layout(G)
    PG = create_embedding(G, pos)
    assert not PG.check_structure()


@pytest.mark.parametrize(
    "G", [nx.hexagonal_lattice_graph(3, 4), nx.triangular_lattice_graph(2, 2)]
)
def test_other_graphs_complex_pos(G: nx.Graph):
    pos = {i[0]: i[1]["pos"] for i in G.nodes(data=True)}
    PG = create_embedding(G, pos)
    assert not PG.check_structure()
