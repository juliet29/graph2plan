import networkx as nx
import pytest

from graph2plan.dcel.original import create_embedding
from graph2plan.fourtp.checks import (
    check_interior_faces_are_triangles,
    check_is_triangulated_chordal,
    Improper4TPGraphError,
    check_is_biconnected,
)

def create_node_positioned_graph(G):
    pos = {i: i for i in G.nodes}
    return G, pos

def test_grid_graph_is_not_triangulated():
    G, pos = create_node_positioned_graph(nx.grid_2d_graph(2, 3))
    with pytest.raises(Improper4TPGraphError):
        PG = create_embedding(G, pos)
        check_interior_faces_are_triangles(PG)


def test_grid_graph_is_not_chordal():
    G = nx.grid_2d_graph(2, 3)
    with pytest.raises(Improper4TPGraphError):
        check_is_triangulated_chordal(G)


def test_triangular_lattice_is_biconnected():
    G = nx.triangular_lattice_graph(2, 3)
    check_is_biconnected(G)


def test_triangular_lattice_is_triangulated():
    G, pos =  create_node_positioned_graph(nx.triangular_lattice_graph(2, 3))
    PG = create_embedding(G, pos)
    check_interior_faces_are_triangles(PG)


def test_triangular_lattice_is_chordal():
    G = nx.triangular_lattice_graph(2, 3)
    check_is_triangulated_chordal(G)
