from copy import deepcopy
from graph2plan.dcel.original import create_embedding
from graph2plan.dual.helpers import (
    get_embedding_faces,
    split_cardinal_and_interior_edges,
)
from graph2plan.helpers.geometry_interfaces import VertexPositions


import networkx as nx


# TODO this all goes elsewhere.. =>combine with dcel when simplify that.. 


# don't delete -> a helper / util fx.. actually can wrap with the earlier asserts.. 
def print_all_cw_nbs(PE: nx.PlanarEmbedding, node: str):
    print(f"cw nbs of {node}: {list(PE.neighbors_cw_order(node))}")



def get_last_cw_nb(PE: nx.PlanarEmbedding, node: str):
    return list(PE.neighbors_cw_order(node))[-1]


def get_first_cw_nb(PE: nx.PlanarEmbedding, node: str):
    return list(PE.neighbors_cw_order(node))[0]


def add_cw_pair(PE: nx.PlanarEmbedding, node, cw_nb):
    PE.add_half_edge_ccw(node, cw_nb, reference_neighbor=get_first_cw_nb(PE, node))
    assert get_first_cw_nb(PE, node) == cw_nb

    PE.add_half_edge_cw(cw_nb, node, reference_neighbor=get_last_cw_nb(PE, cw_nb))
    assert get_last_cw_nb(PE, cw_nb) == node
    return PE


# TODO use CDE class names, # TODO replace dcel.external with this..
def add_exterior_embed(_PE: nx.PlanarEmbedding):
    PE = deepcopy(_PE)
    PE = add_cw_pair(PE, "v_n", "v_e")
    PE = add_cw_pair(PE, "v_e", "v_s")
    PE = add_cw_pair(PE, "v_s", "v_w")
    PE = add_cw_pair(PE, "v_w", "v_n")
    PE = add_cw_pair(PE, "v_n", "v_s")  # think about this a bit...
    PE.check_structure()

    return PE



def get_embedding_of_four_complete_G(G: nx.Graph, full_pos: VertexPositions):
    _, interior = split_cardinal_and_interior_edges(G)
    PE_interior = create_embedding(nx.edge_subgraph(G, interior), full_pos)
    return add_exterior_embed(PE_interior)



def get_external_face(PE: nx.PlanarEmbedding, full_pos: VertexPositions):
    faces = get_embedding_faces(PE)
    # all faces should have length 3 or greater -> may want to generalize.. 
    for face in faces:
        assert face.n_vertices >= 3, f"Face: {face} has less than 3 vertices!"


    return sorted(faces, key=lambda x: x.get_area(full_pos), reverse=True)[0]




