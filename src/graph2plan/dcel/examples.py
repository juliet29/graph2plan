import networkx as nx

from ..helpers.graph_interfaces import VertexPositions

""" example from DeBerg s2.2 on doubly connected edge list (dcel) """


def draw_deberg(G: nx.Graph, plot=False):
    pos = VertexPositions({1: (0, 4), 2: (2, 4), 3: (2, 2), 4: (1, 1)})
    if plot:
        nx.draw_networkx(G, pos)

    return pos


def deberg(plot=False):
    G: nx.Graph[int] = nx.Graph()
    G.add_edge(1, 2)  # e11
    G.add_edge(3, 4)  # e21
    G.add_edge(3, 1, ccw=4)  # e31
    G.add_edge(3, 2, ccw=1)  # e41

    pos = draw_deberg(G, plot)

    return G, pos


def deberg_embedded():
    G = nx.PlanarEmbedding()

    G.add_half_edge_first(1, 2)  # e11
    G.add_half_edge_first(2, 1)  # e12

    G.add_half_edge_first(3, 4)  # e21
    G.add_half_edge_first(4, 3)  # e22

    G.add_half_edge_cw(3, 1, reference_neighbor=4)  # e31
    G.add_half_edge_cw(1, 3, reference_neighbor=2)  # e32

    G.add_half_edge_cw(3, 2, reference_neighbor=1)  # e41
    G.add_half_edge_cw(2, 3, reference_neighbor=1)  # e42

    draw_deberg(G)

    G.check_structure()

    return G
