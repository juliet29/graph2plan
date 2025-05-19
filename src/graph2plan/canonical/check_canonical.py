from itertools import permutations

import networkx as nx

from .canonical_interfaces import CanonicalOrderingFailure

from ..helpers.utils import set_intersection
from .canonical_interfaces import CanonicalOrder, G_canonical


def is_Gk_minus_1_biconnected(G: nx.Graph, co: CanonicalOrder):
    if len(co.Gk_minus_1_nodes()) >= 3:
        Gk_minus_1 = G.subgraph(co.Gk_minus_1_nodes())
        if not nx.is_biconnected(Gk_minus_1):
            raise CanonicalOrderingFailure
    else:
        print(
            f">>Biconnection check: Skipping, < 3 vertices in Gk-1, currently have {co.Gk_minus_1_nodes()}..."
        )
        return

    # print(">>Biconnection check: passed")


# TODO clean up logic
def are_u_v_in_Ck(G_c: G_canonical, co: CanonicalOrder):
    if co.u not in co.Gk_nodes or co.v not in co.Gk_nodes:
        raise CanonicalOrderingFailure("Initial nodes not in Gk")

    outer_face = G_c.outer_face_at_k(co)
    if co.u not in outer_face or co.v not in outer_face:
        raise CanonicalOrderingFailure(
            f"{co.u} or {co.v} not in outer_face: {outer_face}"
        )
    # print(">>u,v in Ck check: passed")


def is_vk_in_Ck(G_c: G_canonical, co: CanonicalOrder, node: str):
    outer_face = G_c.outer_face_at_k(co)
    if node not in outer_face:
        raise CanonicalOrderingFailure(f"Vk `{node}` not in outer face: {outer_face}")
    # print(">>vk in Ck check: passed")


def do_vk_nbs_form_2v_subinterval_in_Ck_minus_1(
    G_c: G_canonical, co: CanonicalOrder, node: str
):
    nbs = list(G_c.G.neighbors(node))
    if not len(nbs) > 2:
        raise CanonicalOrderingFailure(f"`{node}` does not have >2 ({nbs})")

    outer_face = G_c.outer_face_at_k_minus_1(co)
    nbs_in_outer_face = set_intersection(nbs, outer_face)
    if not len(nbs_in_outer_face) >= 2:
        raise CanonicalOrderingFailure(
            f"`{node}` does not have >2 nbs in Ck-1({nbs_in_outer_face})"
        )

    Gcycle = nx.cycle_graph(outer_face, nx.Graph)
    for p in permutations(nbs_in_outer_face):
        if nx.is_simple_path(Gcycle, p):
            # print(">>vk nbs form 2v subinterval in Ck-1 check: passed")
            return

    raise CanonicalOrderingFailure(
        f"Nbs of `{node}` ({nbs_in_outer_face}) do not form path in Ck-1: {outer_face}"
    )


def does_vk_have_2plus_nbs_in_G_diff_Gk_minus_1(
    G_c: G_canonical, co: CanonicalOrder, node: str
):
    if co.k > co.n - 2:
        print(
            f">>vk has 2+ nbs in G-(Gk-1) check:  Skipping since  k ({co.k}) > n-2 ({co.n - 2})..."
        )
        return

    # TODO repeated in previous check, can pull out..
    nbs = list(G_c.G.neighbors(node))
    if not len(nbs) >= 2:
        raise CanonicalOrderingFailure(f"`{node}` does not have >= 2 ({nbs})")

    if not len(set_intersection(co.G_diff_Gk_minus_1_nodes, nbs)) >= 2:
        raise CanonicalOrderingFailure(
            f"`{node}` does not have >=2 ({nbs}) in G-(Gk-1) ({nbs})"
        )

    # print(">>vk has 2+ nbs in G-(Gk-1) check: passed")


def vk_permits_valid_order(G_c: G_canonical, co: CanonicalOrder, node: str):
    is_Gk_minus_1_biconnected(G_c.G, co)
    are_u_v_in_Ck(G_c, co)
    is_vk_in_Ck(G_c, co, node)
    do_vk_nbs_form_2v_subinterval_in_Ck_minus_1(G_c, co, node)
    does_vk_have_2plus_nbs_in_G_diff_Gk_minus_1(G_c, co, node)
