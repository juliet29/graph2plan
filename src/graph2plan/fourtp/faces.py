from copy import deepcopy

import networkx as nx
from networkx import NetworkXError, NetworkXException

from graph2plan.dcel.original import create_embedding
from graph2plan.dual.helpers import (
    EmbeddingError,
    get_embedding_faces,
    split_cardinal_and_interior_edges,
)
from graph2plan.helpers.geometry_interfaces import CoordinateList, VertexPositions

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
    PE = add_cw_pair(PE, "v_s", "v_n")  # think about this a bit...
    PE.check_structure()

    return PE


def get_embedding_of_four_complete_G(G: nx.Graph, full_pos: VertexPositions):
    _, interior = split_cardinal_and_interior_edges(G)
    PE_interior = create_embedding(nx.edge_subgraph(G, interior), full_pos)
    return add_exterior_embed(PE_interior)


def get_external_face(PE: nx.PlanarEmbedding, full_pos: VertexPositions):
    """
    Assumptions: the graphs interior is triangulated, while the exterior may or may not be. Chords may or may not exist. In the ideal case where there are no chords and fully triangulated =>
    https://cs.stackexchange.com/questions/116518/given-a-dcel-how-do-you-identify-the-unbounded-face"""

    # TODO better logic -> cant do if there are chords + fully triangulated..
    if PE.order() <= 3:
        return list(PE.nodes)

    all_faces = get_embedding_faces(PE)
    triangular_faces = [len(face.vertices) == 3 for face in all_faces]

    if all(triangular_faces):
        # use this approach if all faces are triangular
        filtered_pos = {k: v for k, v in full_pos.items() if k in PE.nodes}
        extreme_node = CoordinateList.name_extreme_coord(filtered_pos)
        left_nb, right_nb = (
            get_first_cw_nb(PE, extreme_node),
            get_last_cw_nb(PE, extreme_node),
        )

        left_face = PE.traverse_face(left_nb, extreme_node)
        right_face = PE.traverse_face(extreme_node, right_nb)

        assert set(left_face) == set(right_face)

        return left_face
    else:
        external_faces = [i for i in all_faces if i.n_vertices > 3]
        assert len(external_faces) == 1, (
            f"Len of external faces > 1: {sorted(external_faces, key=lambda i: i.n_vertices)}"
        )
        # print(external_faces[0])
        return external_faces[0].vertices

    # if all faces are triangular except one, then non-triangulated is external

    # try:
    # faces = get_embedding_faces(PE)
    # # except EmbeddingError:
    # #     try:
    # #         PE.check_structure()
    # #     except NetworkXException:

    # #         raise Exception("There is something wrong with the embedding..")
    # # all faces should have length 3 or greater -> may want to generalize..

    # for face in faces:
    #     assert face.n_vertices >= 3, f"Face: {face} has less than 3 vertices!"

    print()
    # return sorted(faces, key=lambda x: x.get_signed_area(full_pos), reverse=True)[0]
