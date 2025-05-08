from numpy import outer
from graph2plan.fourtp.canonical_interfaces import CanonicalOrder
from graph2plan.fourtp.canonical_interfaces import G_canonical


import networkx as nx


def is_Gk_minus_1_biconnected(G: nx.Graph, co: CanonicalOrder):
    if len(co.Gk_minus_1_nodes) >= 3:
        Gk_minus_1 = G.subgraph(co.Gk_minus_1_nodes)
        assert nx.is_biconnected(Gk_minus_1)
        print(">>Biconnection check: passed")
    else:
        print(f">>Biconnection check: Skipping, >=3 vertices in Gk-1, currently have {co.Gk_minus_1_nodes}...")


def are_u_v_in_Ck(G_c: G_canonical, co: CanonicalOrder):
    assert (
        co.u in co.Gk_nodes and co.v in co.Gk_nodes
    )  # TODO need to be in external face! need to calculate an embedding!
    outer_face = G_c.outer_face_at_k(co)
    assert co.u in outer_face and co.v in outer_face, f">>Ck check: {co.u} or {co.v} not in outer_face: {outer_face}"
    print(">>Ck check: passed")



def do_vk_nbs_form_2v_subinterval_in_Ck_minus_1():
    pass


def does_vk_have_2plus_nbs_in_G_diff_Gk_minus_1():
    pass
