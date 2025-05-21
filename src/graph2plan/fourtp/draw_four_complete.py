from copy import deepcopy
import matplotlib.pyplot as plt
import networkx as nx
import shapely as shp
from matplotlib.patches import FancyArrowPatch
from matplotlib.transforms import Bbox

from graph2plan.dual.helpers import split_cardinal_and_interior_edges
from graph2plan.fourtp.four_complete import CardinalPath
from graph2plan.helpers.geometry_interfaces import ShapelyBounds
from graph2plan.helpers.graph_interfaces import get_vertex_name, VertexPositions


def compute_and_draw_edges(G, pos, full_pos, ax):
    cardinal_edges, interior_edges = split_cardinal_and_interior_edges(G)

    graph_points = list(pos.values())
    boundary = shp.MultiPoint(graph_points).convex_hull
    sb = ShapelyBounds(*boundary.bounds)
    bbox = Bbox.from_extents(sb.min_x, sb.min_y, sb.max_x, sb.max_y)

    arcs = []
    rad = -0.3
    for edge in cardinal_edges:
        source, target = edge
        posA, posB = full_pos[source], full_pos[target]
        arc = f"arc3,rad={rad}"
        arrow = FancyArrowPatch(posA, posB, connectionstyle=arc)
        res = arrow.get_path().intersects_bbox(bbox)
        if not res:
            arcs.append((edge, arc))
        else:
            arc = f"arc3,rad={rad * -1}"
            arcs.append((edge, arc))

    nx.draw_networkx_edges(G, full_pos, edgelist=interior_edges, ax=ax)
    for edge, arc in arcs:
        nx.draw_networkx_edges(
            G,
            full_pos,
            edgelist=[edge],
            style="dashed",
            edge_color="pink",
            connectionstyle=arc,
            ax=ax,
            arrows=True,
        )


def draw_four_complete_graph(G, pos, full_pos, nodelist=None, fig_label=""):
    fig, ax = plt.subplots(1, 1)
    compute_and_draw_edges(G, pos, full_pos, ax)
    nx.draw_networkx_nodes(G, full_pos, ax=ax, nodelist=nodelist)
    nx.draw_networkx_labels(G, full_pos, ax=ax)

    return ax


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
