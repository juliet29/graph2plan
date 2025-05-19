from copy import deepcopy
import networkx as nx
import pytest

from graph2plan.dcel.original import create_embedding
from graph2plan.helpers.graph_checks import (
    check_interior_faces_are_triangles,
    check_is_4_connected,
    check_is_triangulated_chordal,
    Improper4TPGraphError,
    Improper3TPGraphError,
    check_is_biconnected,
    check_is_valid_triangulated
)

def create_node_positioned_graph(G):
    # TODO share with other tests in test_embedding... (maybe)
    pos = {i: i for i in G.nodes}
    return G, pos

# TOD test biconnected

def test_grid_graph_is_not_triangulated():
    G, pos = create_node_positioned_graph(nx.grid_2d_graph(2, 3))
    with pytest.raises(Improper3TPGraphError):
        PG = create_embedding(G, pos)
        check_interior_faces_are_triangles(PG)



def test_grid_graph_is_not_chordal():
    G = nx.grid_2d_graph(2, 3)
    with pytest.raises(AssertionError):
        check_is_triangulated_chordal(G)

def test_triangular_lattice_is_valid_triangulated():
    G, pos =  create_node_positioned_graph(nx.triangular_lattice_graph(2, 3))
    check_is_valid_triangulated(G, pos)
# TODO G, pos =  draw_node_positioned_graph(nx.triangular_lattice_graph(2, 3)) is not 4 connected.. 

@pytest.mark.skip(reason="not working as expected.. ")
def test_augmented_graph_is_not_valid_triangulated():
    G =nx.triangular_lattice_graph(4,4)
    G1 = deepcopy(G)
    G1.add_edges_from(nx.k_edge_augmentation(G, 4))
    pos_planar = nx.planar_layout(G1)
    # TODO test that it is 4 connected
    with pytest.raises(Improper3TPGraphError):
        check_is_valid_triangulated(G, pos=pos_planar)


# TODO use hypothesis to try on all the graphs.. 
def test_random_regular_graph_is_valid_4_connected():
    G = nx.random_regular_graph(4,6, seed=1) # all generated graphs will be isomorphic
    # (4, 8 and above) does not possess a planar embedding.. 
    check_is_4_connected(G)
    planarity_check, PG  = nx.check_planarity(G)
    assert planarity_check
    with pytest.raises(Improper3TPGraphError, match="There are seperating triangles"):
        check_is_valid_triangulated(G, PG=PG)
    # TODO inconsistency between separating triangles and 4-connected check?
    check_is_4_connected(PG)
