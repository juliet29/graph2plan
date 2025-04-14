from ..dcel.interfaces import EmbedResult
from ..helpers.graph_interfaces import Axis
from .helpers import check_correct_n_faces_in_edge_face_dict
from .create_domains import calculate_domains
from .create_dual import create_dual, draw_dual, prep_dual


def create_dual_and_calculate_domains(
    embed_result: EmbedResult, axis: Axis, draw=False
):
    if draw:
        embed_result.draw()
    faces = prep_dual(embed_result.embedding, embed_result.directed_edges)
    check_correct_n_faces_in_edge_face_dict(faces)
    dual_graph, dual_pos = create_dual(faces, embed_result.pos, axis)
    if draw:
        draw_dual(dual_graph, dual_pos)
    domains = calculate_domains(
        dual_graph, embed_result.embedding, embed_result.directed_edges, axis
    )
    return domains
