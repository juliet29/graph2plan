import random
from collections import deque
from copy import deepcopy
from enum import Enum
from pprint import pprint
from typing import Literal, NamedTuple

import networkx as nx
import shapely as shp

from graph2plan.dcel.original import create_embedding
from graph2plan.fourtp.draw_four_complete import draw_four_complete_graph
from graph2plan.fourtp.faces import get_external_face
from graph2plan.helpers.graph_checks import Improper4TPGraphError, check_is_k_connected
from graph2plan.helpers.utils import get_unique_items_in_list_keep_order

from ..helpers.geometry_interfaces import T, VertexPositions
from ..helpers.graph_interfaces import CardinalDirectionEnum as CDE
from ..helpers.graph_interfaces import cardinal_directions, get_vertex_name
from ..helpers.utils import NotImplementedError, chain_flatten

"""Four-completion algorithm from Koz+Kim'85, to take a triangulated graph and make it four completed... Currently only works if exterior face has at least 4 nodes"""


class Alphas(Enum):
    NE = 0
    SE = 1
    SW = 2
    NW = 3


alpha_mapping: dict[CDE, tuple[Alphas, Alphas]] = {
    # counter clockwise orientation here
    CDE.NORTH: (Alphas.NW, Alphas.NE),
    CDE.EAST: (Alphas.NE, Alphas.SE),
    CDE.SOUTH: (Alphas.SE, Alphas.SW),
    CDE.WEST: (Alphas.SW, Alphas.NW),
}


class CardinalPath(NamedTuple):
    drn: CDE
    path: list

    def __repr__(self) -> str:
        return f"{(self.drn.name, self.path)}"


def place_cardinal(_pos: VertexPositions, path_pairs: list[CardinalPath]):
    def get_location(path):
        path_points = [pos[i] for i in path]

        path_centroid = shp.MultiPoint(path_points).centroid

        line = shp.shortest_line(path_centroid, boundary)
        drn_location = [i for i in line.coords][1]
        assert len(drn_location) == 2
        return drn_location
        # pos[get_vertex_name(drn)] = drn_location
        # return p

    pos = deepcopy(_pos)
    graph_points = list(pos.values())
    # TODO compute distance based on VertexPositions, 1 may be too far or not far enough..
    boundary = (
        shp.MultiPoint(graph_points)
        .convex_hull.buffer(distance=1, quad_segs=1)
        .exterior
    )
    for pair in path_pairs:
        drn, path = pair
        pos[get_vertex_name(drn)] = get_location(path)

    return pos


def choose_alphas(outer_face: list[T]):
    # outer face should be clockwise!
    random.seed(3)
    N_NODES = 4
    assert (
        len(outer_face) >= N_NODES
    )  # TODO adress the case when there are three.. / deal with case of max assigning two alphas to a node on external boundary..
    # also think  about the case for two and one..
    selected_nodes = sorted(random.sample(outer_face, N_NODES), key=outer_face.index)
    return {alpha: node for alpha, node in zip(Alphas, selected_nodes)}


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
    G_cycle: nx.DiGraph, pos: VertexPositions, alpha_node_mapping: dict[Alphas, T]
):
    def find_card_drn_path(drn):
        alpha1, alpha2 = alpha_mapping[drn]
        node1 = alpha_node_mapping[alpha1]
        node2 = alpha_node_mapping[alpha2]
        path = nx.shortest_path(G_cycle, node1, node2)
        return CardinalPath(drn, path)

    path_pairs = [find_card_drn_path(drn) for drn in CDE]

    check_paths_are_correct(G_cycle, path_pairs)

    path_pairs = orient_paths(pos, path_pairs)
    # pprint(path_pairs)

    return path_pairs


def four_complete(_G: nx.Graph, pos: VertexPositions, outer_face: list[str]):
    alpha_node_mapping = choose_alphas(outer_face)
    # print({k.name: v for k, v in alpha_node_mapping.items()})

    G_cycle = nx.cycle_graph(outer_face, nx.DiGraph)
    path_pairs = find_paths(G_cycle, pos, alpha_node_mapping)
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

    try:
        check_is_k_connected(G, 3)
        check_is_k_connected(G, 4)
    except Improper4TPGraphError:
        full_pos = place_cardinal(pos, path_pairs)
        draw_four_complete_graph(G, pos, full_pos)

    return G, path_pairs


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


def add_points_on_shortcuts(
    _G: nx.Graph, _pos: VertexPositions, shortcuts: list[tuple[str]]
):
    def get_coord_of_new_point(shortcut: tuple[str]):
        path_points = [pos[i] for i in shortcut]
        print(path_points)
        middle_point = (
            shp.LineString(path_points).interpolate(0.5, normalized=True).coords[0]
        )
        print(middle_point)
        assert len(middle_point) == 2
        return middle_point

    def add_new_point(shortcut: tuple[str]):
        new_node = G.order() + 1
        G.add_edges_from([(i, new_node) for i in shortcut])
        pos[new_node] = get_coord_of_new_point(shortcut)

    G = deepcopy(_G)
    pos = deepcopy(_pos)
    for sc in shortcuts:
        add_new_point(sc)

    nx.draw_networkx(G, pos)

    return G, pos


def graph_to_four_complete(G: nx.Graph, pos: VertexPositions):
    PE = create_embedding(G, pos)
    outer_face = get_external_face(PE, pos)
    shortcuts = check_for_shortcuts(G, outer_face)
    print(shortcuts)
    add_points_on_shortcuts(G, pos, shortcuts)
    # check for short cuts..
    # four_complete(G, pos, outer_face)
