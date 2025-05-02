
import networkx as nx
from random import sample

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
    G.add_edges_from(v5_edges + v6_edges + v0_edges + v4_edges + v2_edges + v3_edges + v1_edges) 

    return G, assign_pos(arrs, shift_value=-1)

def kk85_outer_face():
    return ["v5", "v6", "v4", "v7", "v1", "v0"]


def choose_alphas(outer_face:list):
    assert len(outer_face) >= 3

    alphas = sample(outer_face, 4)
    return sorted(alphas, key = outer_face.index)

    

def four_complete(G, pos, outer_face): 
    alphas = choose_alphas(outer_face)
    

    # choose 4 points on outerface to be alphas
        # choose 4 random, and then order based on outerface order.. 
    # get the paths between the alphas (inclusive)
    # r => [ur, br] ~ e
    # b => [br, bl] ~ s
    # l => [bl, ul] ~ w
    # u => [ul, ur] ~ n 
    # add edges according to above 
    # place nodes 
