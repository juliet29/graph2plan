from itertools import cycle
import random
from collections import deque
from copy import deepcopy
from pprint import pprint
from typing import Literal

import networkx as nx
import shapely as shp

from graph2plan.dcel.original import create_embedding
from graph2plan.fourtp.draw_four_complete import (
    draw_four_complete_graph,
    place_cardinal,
)
from graph2plan.fourtp.faces import get_external_face
from graph2plan.fourtp.interfaces import Alphas, CardinalPath, alpha_mapping
from graph2plan.helpers.graph_checks import Improper4TPGraphError, check_is_k_connected
from graph2plan.helpers.utils import get_unique_items_in_list_keep_order

from ..helpers.geometry_interfaces import T, VertexPositions
from ..helpers.graph_interfaces import CardinalDirectionEnum as CDE
from ..helpers.graph_interfaces import cardinal_directions, get_vertex_name
from ..helpers.utils import NotImplementedError, chain_flatten

"""Four-completion algorithm from Koz+Kim'85, to take a triangulated graph and make it four completed... Currently only works if exterior face has at least 4 nodes"""


def choose_alphas(outer_face: list[T], SEED=3) -> dict[Alphas, T]:
    # outer face should be clockwise!
    random.seed(SEED)
    N_NODES = len(outer_face)
    if N_NODES >3:
        selected_nodes = sorted(
            random.sample(outer_face, N_NODES), key=outer_face.index
        )
        return {alpha: node for alpha, node in zip(Alphas, selected_nodes)}
    else:
        face = deque(outer_face)
        print(f"==>> face: {face}")
        
        rotation_num = 0 # random.randint(0, 2)
        face.rotate(rotation_num)
        print(f"==>> face afyer rotate: {face}")
        # face.reverse()
        # print(f"==>> face afyer reverse: {face}")

        if N_NODES == 3 or N_NODES == 1:
            return {alpha: node for alpha, node in zip(Alphas, cycle(face))}
        elif N_NODES == 2:
            face_iter = list(face) + list(reversed(face))
            return {alpha: node for alpha, node in zip(Alphas, face_iter)}
        else:
            raise Exception(f"Invalid outer face with len {N_NODES}")


def check_paths_are_correct(G_cycle: nx.DiGraph, path_pairs: list[CardinalPath]):
    # check is correct
    joint_path = get_unique_items_in_list_keep_order(
        chain_flatten([p.path for p in path_pairs])
    )
    assert len(joint_path) == G_cycle.order()
    assert nx.is_simple_path(G_cycle, joint_path)


def orient_paths(pos: VertexPositions, path_pairs: list[CardinalPath]):
    def get_path_y(path):
        path_points = [pos[i] for i in path]
        path_centroid = shp.MultiPoint(path_points).centroid
        return path_centroid.y

    south_path = sorted(path_pairs, key=lambda p: get_path_y(p.path))[0]
    south_path_ix = path_pairs.index(south_path)

    vertex_order = deque([p.drn for p in path_pairs])
    while vertex_order.index(CDE.SOUTH) != south_path_ix:
        vertex_order.rotate(1)

    original_paths = [p.path for p in path_pairs]

    return [CardinalPath(drn, path) for drn, path in zip(vertex_order, original_paths)]


def find_paths(
    G_cycle: nx.DiGraph, alpha_node_mapping: dict[Alphas, T], pos: VertexPositions 
):
    def find_card_drn_path(drn):
        alpha1, alpha2 = alpha_mapping[drn]
        node1 = alpha_node_mapping[alpha1]
        node2 = alpha_node_mapping[alpha2]
        path = nx.shortest_path(G_cycle, node1, node2)
        return CardinalPath(drn, path)

    path_pairs = [find_card_drn_path(drn) for drn in CDE]

    check_paths_are_correct(G_cycle, path_pairs)

    # path_pairs = orient_paths(pos, path_pairs)

    return path_pairs


def four_complete(_G: nx.Graph, pos: VertexPositions, outer_face: list[str]):
    alpha_node_mapping = choose_alphas(outer_face)
    # print({k.name: v for k, v in alpha_node_mapping.items()})

    G_cycle = nx.cycle_graph(outer_face, nx.DiGraph)
    path_pairs = find_paths(G_cycle, alpha_node_mapping, pos)
    # can find the path that is most south, and assign that to be south, then move other along ..

    G = deepcopy(_G)
    for pair in path_pairs:
        drn_data = cardinal_directions[pair.drn]
        if drn_data.orientation == "IN":
            G.add_edges_from(
                [(cycle_node, drn_data.vertex_name) for cycle_node in pair.path]
            )
        else:
            G.add_edges_from(
                [(cycle_node, drn_data.vertex_name) for cycle_node in pair.path]
            )

    # TODO at this point, distinguish between interior and exterior edges.. with an attribute..
    # TODO should just have these edges as a list saved somewhere.. see where else this is used..
    G.add_edge(get_vertex_name(CDE.SOUTH), get_vertex_name(CDE.EAST))
    G.add_edge(get_vertex_name(CDE.SOUTH), get_vertex_name(CDE.WEST))
    G.add_edge(get_vertex_name(CDE.WEST), get_vertex_name(CDE.NORTH))
    G.add_edge(get_vertex_name(CDE.EAST), get_vertex_name(CDE.NORTH))

    # apparently adding an edge between non-adjacent nodes is enough to four-complete (from kant + he)
    G.add_edge(get_vertex_name(CDE.SOUTH), get_vertex_name(CDE.NORTH))

    full_pos = place_cardinal(pos, path_pairs)
    draw_four_complete_graph(G, pos, full_pos)
    try:
        check_is_k_connected(G, 3)
        check_is_k_connected(G, 4)
    except Improper4TPGraphError:
        print("Graph is NOT 4-connected!!")

    return G, full_pos


def check_for_shortcuts(G: nx.Graph, outer_face: list[str]):
    shortcuts = []
    G_outer = nx.cycle_graph(outer_face, nx.Graph)
    for u, v in G.edges:
        if u in outer_face and v in outer_face:
            if (u, v) not in G_outer.edges:
                shortcuts.append((u, v))

    if len(shortcuts) >= 4:
        raise NotImplementedError(
            f"Possibility of having more than 4 corner implying paths, but haven't implemented check for this: {shortcuts}. n_shortcuts={len(shortcuts)}"
        )

    return shortcuts


# TODO tuple[str, str] -> edge
Edge = tuple[str, str]


def graph_to_four_complete(G: nx.Graph, pos: VertexPositions):
    PE = create_embedding(G, pos)
    if G.order() <= 2:
        outer_face = list(G.nodes) # need to organize them clockwise.. 
    else:
        outer_face = get_external_face(PE, pos)

    shortcuts = check_for_shortcuts(G, outer_face)
    # print(f"==>> shortcuts: {shortcuts}")
    if shortcuts and len(outer_face) >= 4:
        raise NotImplementedError("Haven't appropiately handled short cuts!")
    # G2, pos2 = add_points_on_shortcuts(G, pos, shortcuts, outer_face)
    # shortcuts2 = check_for_shortcuts(G2, outer_face)
    # assert len(shortcuts2) == 0, (
    #     f"There should be no shortcuts, but now we have: {shortcuts2}"
    # )

    return four_complete(G, pos, outer_face)
