from graph2plan.dcel.external import fully_embed_graph
import networkx as nx
from graph2plan.dual.interfaces import Domain, Domains, VertexDomain
from graph2plan.helpers.geometry_interfaces import ShapelyBounds, VertexPositions
from ..dcel.interfaces import EmbedResult
from ..helpers.graph_interfaces import Axis
from .calculate_domains import calculate_domains
from .create_dual import create_dual, draw_dual, prep_dual
from .helpers import check_correct_n_faces_in_edge_face_dict


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


def merge_domains(
    x_domains: dict[str, VertexDomain], y_domains: dict[str, VertexDomain]
):
    domains = []
    assert x_domains.keys() == y_domains.keys()
    for key in x_domains.keys():
        xdom = x_domains[key]
        ydom = y_domains[key]
        domains.append(
            Domain(
                name=key,
                bounds=ShapelyBounds(
                    min_x=xdom.min, min_y=ydom.min, max_x=xdom.max, max_y=ydom.max
                ),
            )
        )

    doms = Domains(domains)
    return doms


def create_floorplan_from_st_graphs(
    T1: nx.DiGraph, T2: nx.DiGraph, pos: VertexPositions
):
    res1 = fully_embed_graph(T1, pos, "y")
    res2 = fully_embed_graph(T2, pos, "x")
    x_domains = create_dual_and_calculate_domains(res1, "y", True)
    y_domains = create_dual_and_calculate_domains(res2, "x", True)
    # TODO may have errors because of orientation..
    merged_doms = merge_domains(x_domains, y_domains)
    merged_doms.draw()

    return merged_doms
