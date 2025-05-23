from graph2plan.canonical.canonical_order import initialize_canonical_order
from graph2plan.dual.helpers import check_is_source_target_graph
from graph2plan.helpers.geometry_interfaces import VertexPositions
import networkx as nx
from graph2plan.dcel.original import create_embedding
from graph2plan.fourtp.faces import get_external_face
from graph2plan.main.tests import create_rel, iterate_canonical_order, create_dual
from graph2plan.rel.draw_rel import plot_rel_base_graph
from graph2plan.rel.rel2 import extract_graphs, initialize_rel_graph
from .four_complete import (
    check_for_shortcuts,
    choose_alphas,
    find_paths,
    four_complete,
    graph_to_four_complete,
)
import random
from itertools import cycle
from collections import deque
import networkx as nx
from ..helpers.auto_pos import create_integer_G_and_pos


def get_shortcuts(G: nx.Graph, pos: VertexPositions):
    PE = create_embedding(G, pos)
    outer_face = get_external_face(PE, pos)
    shortcuts = check_for_shortcuts(G, outer_face)
    return shortcuts, outer_face


def test_alpha_selections(SEED=0):
    outer_face = deque("a b c".split())
    G_cycle = nx.cycle_graph(outer_face, nx.DiGraph)
    # glue together backwards if len == 2, instead of cycling..

    random.seed(SEED)

    outer_face.rotate(random.randint(0, 2))
    print(f"==>> outer_face: {outer_face}")

    alphas = "ne se sw nw".split()
    face_cycle = cycle(outer_face)
    # randomness comes from rotating this a certain amount..
    for alpha, vertex in zip(alphas, face_cycle):
        print(alpha, vertex)


def test_degen_cycle(SEED=0):
    outer_face = "c a b".split()  # issue bc the embedding coming automatically, but have chance to explore cw vs not cw external face embedding..
    positions = [(0, 1), (1, 0), (0, 0)]
    pos = VertexPositions({k: v for k, v in zip(outer_face, positions)})
    # G_cycle = nx.cycle_graph(outer_face, nx.DiGraph)
    G_cycle = nx.DiGraph()
    G_cycle.add_edges_from([("c", "a"), ("a", "b"), ("b", "c")])

    nx.draw_networkx(G_cycle, pos)
    alpha_node_mapping = choose_alphas(outer_face, SEED)
    print(f"==>> alpha_node_mapping: {alpha_node_mapping}")

    path_pairs = find_paths(G_cycle, alpha_node_mapping, pos)
    print(f"==>> path_pairs: {path_pairs}")

    Gfc, full_pos = four_complete(G_cycle, pos, outer_face)
    G_c, co = initialize_canonical_order(Gfc, pos, full_pos)
    G_c, co = iterate_canonical_order(G_c, co)
    print(f"==>> after canon G_c.edges: {G_c.G.edges}")

    Grel = create_rel(G_c.G, co.co_vertices, G_c.embedding)
    print(f"==>> Grel edges: {Grel.edges}")

    T1, T2 = extract_graphs(Grel)
    plot_rel_base_graph(Grel, full_pos, co.co_vertices, (T1, T2))
    check_is_source_target_graph(T1)
    check_is_source_target_graph(T2)
    merged_doms = create_dual(Grel, T1, T2, full_pos)

    return G_c, co


def test_three_graph():
    G, pos = create_integer_G_and_pos(nx.triangular_lattice_graph(1, 1))
    return graph_to_four_complete(G, pos)


def test_two_graph():
    G = nx.Graph()
    G.add_nodes_from([1, 2])
    G.add_edge(1, 2)

    pos = VertexPositions({1: (0, 0), 2: (1, 0)})
    return graph_to_four_complete(G, pos)


def test_one_graph():
    G = nx.Graph()
    G.add_node(1)
    pos = VertexPositions({1: (0, 0)})
    return graph_to_four_complete(G, pos)
