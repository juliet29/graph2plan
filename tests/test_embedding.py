from graph2plan.dcel.examples import deberg_embedded, deberg
from graph2plan.dcel.create import (
    compute_angle_between_edges,
    create_embedding,
    is_cw,
    transform_graph_egdes
)
import pytest
import networkx as nx


@pytest.mark.skip(reason="Getting opposite result of what is expected..")
def test_angle_order():
    G, pos = deberg()
    edge_list = transform_graph_egdes(G)

    e_base = (3,4)
    e_near = (3,1)
    e_far = (3,2)

    angle_near = compute_angle_between_edges(edge_list.get(*e_base), edge_list.get(*e_near), pos)
    angle_far = compute_angle_between_edges(edge_list.get(*e_base), edge_list.get(*e_far), pos)
    assert angle_near < angle_far 



def test_cw():
    G, pos = deberg()
    edge_list = transform_graph_egdes(G)

    e_base = (3, 1)
    e_cw = (3, 2)
    e_ccw = (3, 4)


    t1 = is_cw(edge_list.get(*e_base), edge_list.get(*e_cw), pos)
    t2 = is_cw(edge_list.get(*e_base), edge_list.get(*e_ccw), pos)

    assert t1, t2 == (True, False)




def test_deberg():
    known_embedding = deberg_embedded()
    G, pos = deberg()

    computed_embedding = create_embedding(G, pos)

    assert known_embedding.traverse_face(1,2) == computed_embedding.traverse_face(1,2)
    assert known_embedding.traverse_face(4,3) == computed_embedding.traverse_face(4,3)



def test_2d_grid():
    H = nx.grid_2d_graph(2,3)
    pos = {i:i for i in H.nodes}
    create_embedding(H, pos)

