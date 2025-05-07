import matplotlib.pyplot as plt
from graph2plan.dual.helpers import split_cardinal_and_interior_edges
from graph2plan.helpers.geometry_interfaces import ShapelyBounds
import networkx as nx
import shapely as shp
from matplotlib.patches import FancyArrowPatch
from matplotlib.transforms import Bbox


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
        )


def draw_four_complete_graph(G, pos, full_pos, nodelist=None, fig_label=""):
    _, ax = plt.subplots(1, 1)
    compute_and_draw_edges(G, pos, full_pos, ax)
    nx.draw_networkx_nodes(G, full_pos, ax=ax, nodelist=nodelist)
    nx.draw_networkx_labels(G, full_pos, ax=ax)
