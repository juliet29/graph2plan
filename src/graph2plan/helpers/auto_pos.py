from copy import deepcopy

import matplotlib.pyplot as plt
import networkx as nx

from graph2plan.helpers.geometry_interfaces import Coordinate, VertexPositions

from .geometry_interfaces import T


def assign_cardinal_pos(arrs: list[list[T]], _pos: dict, delta_x: int, delta_y: int):
    max_len = max([len(i) for i in arrs])
    n_arrs = len(arrs)

    pos = deepcopy(_pos)
    default_y = n_arrs / 2
    default_x = max_len / 2
    init_x = init_y = 0

    pos["v_w"] = Coordinate(init_x, default_y)
    pos["v_e"] = Coordinate(max_len + delta_x + 1, default_y)

    pos["v_s"] = Coordinate(default_x, init_y)
    pos["v_n"] = Coordinate(default_x, n_arrs + delta_y)
    return pos


def assign_pos(
    arrs: list[list[T]], shift_value=1, ASSIGN_CARDINAL=False
) -> VertexPositions:
    pos = {}
    delta_x = delta_y = 1

    if ASSIGN_CARDINAL:
        pos = assign_cardinal_pos(arrs, pos, delta_x, delta_y)

    for level, arr in enumerate(arrs):
        shift = shift_value if level % 2 else 0
        for ix, vertex in enumerate(arr):
            x = ix + delta_x + shift
            y = level + delta_y
            pos[vertex] = Coordinate(x, y)

    return VertexPositions({k: v.pair for k, v in pos.items()})


def create_G_and_pos(G, draw=True):
    pos = {i: i for i in G.nodes}
    if draw:
        nx.draw_networkx(G, pos)
    return G, pos


def draw_node_positioned_graph(G):
    pos = {i: i for i in G.nodes}
    plt.figure()
    nx.draw_networkx(G, pos)
    return G, pos


def create_integer_G_and_pos(_G, draw=True, ADD_V=False) -> tuple[nx.Graph, VertexPositions]:
    G = nx.convert_node_labels_to_integers(_G)
    if ADD_V:
        pos = {name: curr_pos for name, curr_pos in zip(G.nodes, _G.nodes)}
    else:
        pos = {name: curr_pos for name, curr_pos in zip(G.nodes, _G.nodes)}
    print(pos)
    if draw:
        nx.draw_networkx(G, pos)
    return G, VertexPositions(pos)