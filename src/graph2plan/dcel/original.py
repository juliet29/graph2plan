import networkx as nx
from networkx import NetworkXException, PlanarEmbedding
from sympy import Line, N, Triangle

from ..helpers.geometry_interfaces import T, VertexPositions
from .interfaces import Edge, EdgeList, transform_graph_egdes


def soft_check_structure(PG: nx.PlanarEmbedding):
    try:
        PG.check_structure()
    except NetworkXException:
        raise Exception("Structure of this embedding is invalid!!!!")


def create_line(edge: Edge, pos: VertexPositions):
    return Line(pos[edge.u], pos[edge.v])


def compute_angle_between_edges(edge1: Edge, edge2: Edge, pos: VertexPositions):
    assert edge1.u == edge2.u, "Assuming lines originate at same "
    "point"

    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    angle = l1.angle_between(l2)
    return N(angle)


def get_closest_successor(
    pos: VertexPositions, curr_edge: Edge[T], succesors: list[Edge[T]]
) -> Edge[T]:
    sorted_edges = sorted(
        succesors, key=lambda x: compute_angle_between_edges(curr_edge, x, pos)
    )
    return sorted_edges[0]


def is_cw(pos: VertexPositions, edge1: Edge, edge2: Edge):
    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    assert l2
    if l1.is_parallel(l2):
        base = l1.points[0]
        other = l2.points[1]
        above = True if base.compare(other) == 1 else False
        return not above
    triangle = Triangle(*l1.points, l2.points[1])
    try:
        assert isinstance(triangle, Triangle)
    except AssertionError:
        print(f"triangle: {triangle}\nl1: {l1}\nl2: {l2}")
        raise Exception

    return True if triangle.area < 0 else False


def add_edge_with_reference(
    pos: VertexPositions, PG: nx.PlanarEmbedding, e: Edge[T], reference: Edge[T]
):
    cw_value = is_cw(pos, e, reference)
    if cw_value:
        PG.add_half_edge_ccw(e.u, e.v, reference_neighbor=reference.v)
    else:
        PG.add_half_edge_cw(e.u, e.v, reference_neighbor=reference.v)

    return PG


def handle_half_edge(
    PG: PlanarEmbedding, pos: VertexPositions, edge_list: EdgeList, e: Edge[T]
):
    if e.u not in PG.nodes:
        PG.add_half_edge_first(e.u, e.v)
        return 1

    successors: list[T] = list(PG.successors(e.u))

    if not successors:
        PG.add_half_edge_first(e.u, e.v)
        return 2

    if len(successors) == 1:
        ref = edge_list.get(e.u, successors[0])

        add_edge_with_reference(pos, PG, e, ref)
        return 3

    try:
        reference = get_closest_successor(
            pos, e, [edge_list.get(e.u, v) for v in successors]
        )
    except AssertionError:
        print(f"Issue when getting successor for e.u: {e.u}")
        raise Exception
    add_edge_with_reference(pos, PG, e, reference)
    return 4


def create_embedding(G: nx.Graph, pos: VertexPositions):
    edge_list = transform_graph_egdes(G)
    PG = nx.PlanarEmbedding()
    for e in edge_list.edges:
        handle_half_edge(PG, pos, edge_list, e)
    soft_check_structure(PG)

    return PG
