import networkx as nx
import random
from typing import Literal, NamedTuple
from enum import Enum
from copy import deepcopy
import shapely as shp
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.transforms import Bbox

from graph2plan.fourtp.checks import check_is_k_connected
from graph2plan.helpers.utils import get_unique_items_in_list_keep_order
from ..helpers.graph_interfaces import CardinalDirectionEnum as CDE
from ..helpers.graph_interfaces import cardinal_directions, get_vertex_name
from ..helpers.geometry_interfaces import T, VertexPositions, ShapelyBounds
from ..helpers.utils import chain_flatten
from pprint import pprint
from graph2plan.fourtp.examples import kk85, kk85_outer_face


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


def choose_alphas(outer_face: list[T]):
    # outer face should be clockwise!
    random.seed(3)
    N_NODES = 4
    assert (
        len(outer_face) >= N_NODES
    )  # TODO adress the case when there are three.. / deal with case of max assigning two alphas to a node on external boundary..
    selected_nodes = sorted(random.sample(outer_face, N_NODES), key=outer_face.index)
    return {alpha: node for alpha, node in zip(Alphas, selected_nodes)}


class CardinalPath(NamedTuple):
    drn: CDE
    path: list

    def __repr__(self) -> str:
        return f"{(self.drn.name, self.path)}"


def check_paths_are_correct(G_cycle: nx.DiGraph, path_pairs: list[CardinalPath]):
    # check is correct
    joint_path = get_unique_items_in_list_keep_order(
        chain_flatten([p.path for p in path_pairs])
    )
    assert len(joint_path) == G_cycle.order()
    assert nx.is_simple_path(G_cycle, joint_path)


def find_paths(G_cycle: nx.DiGraph, alpha_node_mapping: dict[Alphas, T]):
    def find_card_drn_path(drn):
        alpha1, alpha2 = alpha_mapping[drn]
        node1 = alpha_node_mapping[alpha1]
        node2 = alpha_node_mapping[alpha2]
        path = nx.shortest_path(G_cycle, node1, node2)
        return CardinalPath(drn, path)

    path_pairs = [find_card_drn_path(drn) for drn in CDE]

    check_paths_are_correct(G_cycle, path_pairs)
    pprint(path_pairs)

    return path_pairs


def four_complete(_G: nx.Graph, outer_face):
    alpha_node_mapping = choose_alphas(outer_face)
    print({k.name: v for k, v in alpha_node_mapping.items()})

    G_cycle = nx.cycle_graph(outer_face, nx.DiGraph)
    path_pairs = find_paths(G_cycle, alpha_node_mapping)

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

    G.add_edge(get_vertex_name(CDE.SOUTH), get_vertex_name(CDE.EAST))
    G.add_edge(get_vertex_name(CDE.SOUTH), get_vertex_name(CDE.WEST))
    G.add_edge(get_vertex_name(CDE.WEST), get_vertex_name(CDE.NORTH))
    G.add_edge(get_vertex_name(CDE.EAST), get_vertex_name(CDE.NORTH))

    # apparently adding an edge between non-adjacent nodes is also enough (from kant + he)
    # G.add_edges_from([(v.vertex_name, "00") for v in cardinal_directions.values()])
    G.add_edge(get_vertex_name(CDE.SOUTH), get_vertex_name(CDE.NORTH))

    check_is_k_connected(G, 3)
    check_is_k_connected(G, 4)

    return G, path_pairs


def draw_cardinal(_pos: VertexPositions, path_pairs: list[CardinalPath]):
    def get_location(path):
        path_points = [pos[i] for i in path]

        # TODO compute distance based on points..

        path_centroid = shp.MultiPoint(path_points).centroid

        line = shp.shortest_line(path_centroid, boundary)
        drn_location = [i for i in line.coords][1]
        assert len(drn_location) == 2
        return drn_location
        # pos[get_vertex_name(drn)] = drn_location
        # return p

    pos = deepcopy(_pos)
    graph_points = list(pos.values())
    boundary = (
        shp.MultiPoint(graph_points)
        .convex_hull.buffer(distance=1, quad_segs=1)
        .exterior
    )
    for pair in path_pairs:
        drn, path = pair
        pos[get_vertex_name(drn)] = get_location(path)

    return pos


def test_four_complete():
    G, pos = kk85()
    G, path_pairs = four_complete(G, kk85_outer_face())
    full_pos = draw_cardinal(pos, path_pairs)

    cardinal_names = [get_vertex_name(i) for i in CDE]
    cardinal_edges = []
    for edge in G.edges():
        source, target = edge
        if source in cardinal_names and target in cardinal_names:
            cardinal_edges.append(edge)
    interior_edges = set(G.edges()).difference(set(cardinal_edges))
    

    graph_points = list(pos.values())
    boundary = shp.MultiPoint(graph_points).convex_hull
    sb = ShapelyBounds(*boundary.bounds)
    bbox = Bbox.from_extents(sb.min_x, sb.min_y, sb.max_x, sb.max_y)

    arcs = []
    rad = -0.3
    for edge in cardinal_edges:
        source, target = edge
        posA = full_pos[source]
        posB = full_pos[target]
        arc=f"arc3,rad={rad}"
        arrow = FancyArrowPatch(posA, posB,connectionstyle=arc )
        res = arrow.get_path().intersects_bbox(bbox)
        if not res:
            arcs.append((edge, arc))
        else:
            arc=f"arc3,rad={rad*-1}"
            arcs.append((edge, arc))

    fig, ax = plt.subplots(1,1)

    nx.draw_networkx_edges(G, full_pos, edgelist=interior_edges, ax=ax)
    for edge, arc in arcs:
        nx.draw_networkx_edges(
            G,
            full_pos,
            edgelist=[edge],
            style="dashed",
            edge_color="pink",
            connectionstyle=arc,
            ax=ax
        )
    nx.draw_networkx_nodes(G, full_pos, ax=ax)
    nx.draw_networkx_labels(G, full_pos, ax=ax)

    return G, full_pos
