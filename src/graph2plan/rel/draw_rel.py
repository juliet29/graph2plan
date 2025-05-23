from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from graph2plan.canonical.canonical_interfaces import CanonicalVertices
from graph2plan.helpers.geometry_interfaces import VertexPositions


import networkx as nx
from matplotlib.axes import Axes


def plot_ordered_nodes(
    G: nx.Graph, pos: VertexPositions, co_vertices: CanonicalVertices, ax: Axes
):
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=400, node_shape="s")
    nx.draw_networkx_labels(
        G,
        pos,
        ax=ax,
        labels={n: f"{co_vertices[n]}\n({n})" for n in G.nodes},
        font_size=8,
    )
    return ax


def plot_rel_edges(T1: nx.DiGraph, T2: nx.DiGraph, pos: VertexPositions, ax: Axes):
    nx.draw_networkx_edges(T1, pos, edge_color="blue", ax=ax, label="T1")
    nx.draw_networkx_edges(T2, pos, edge_color="red", ax=ax, label="T2")
    nx.draw_networkx_edge_labels(
        T1,
        pos,
        edge_labels={
            (u, v): data["basis"] for u, v, data in T1.edges(data=True) if data
        },
    )

    nx.draw_networkx_edge_labels(
        T2,
        pos,
        edge_labels={
            (u, v): data["basis"] for u, v, data in T2.edges(data=True) if data
        },
    )

    legend_elements = [
        Line2D([0], [0], color="blue", lw=2, label="T1"),
        Line2D([0], [0], color="red", lw=2, label="T2"),
    ]

    # Add the legend to the plot
    plt.legend(handles=legend_elements, title="Edge Types")


def plot_rel_base_graph(
    G: nx.DiGraph, pos: VertexPositions, co_vertices: CanonicalVertices, st_graphs=None
):
    fig, ax = plt.subplots()
    plot_ordered_nodes(G, pos, co_vertices, ax)
    if st_graphs:
        T1, T2 = st_graphs
        plot_rel_edges(T1, T2, pos, ax)
    else:
        nx.draw_networkx_edges(G, pos)

    plt.show()
