import networkx as nx

from graph2plan.helpers.auto_pos import assign_pos


def kk85():
    l1 = ["v5", "v6"]
    l2 = ["v0", "v2", "v3", "v4"]
    l3 = ["v1", "v7"]
    arrs = [l1, l2, l3]

    v5_edges = [("v5", i) for i in ["v0", "v2", "v3", "v6"]]
    v6_edges = [("v6", i) for i in ["v3", "v4"]]
    v0_edges = [("v0", i) for i in ["v1", "v2"]]
    v2_edges = [("v2", i) for i in ["v1", "v3"]]
    v3_edges = [("v3", i) for i in ["v1", "v7", "v4"]]
    v1_edges = [("v1", "v7")]
    v4_edges = [("v4", "v7")]

    G = nx.DiGraph()
    G.add_edges_from(
        v5_edges + v6_edges + v0_edges + v4_edges + v2_edges + v3_edges + v1_edges
    )

    return G, assign_pos(arrs, shift_value=-1)


def kk85_outer_face():
    return ["v4", "v6", "v5", "v0", "v1", "v7"]

