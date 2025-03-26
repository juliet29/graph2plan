import networkx as nx
from sympy import Line, Triangle, N

from graph2plan.dcel.interfaces import VertexPositions, transform_graph_egdes
from .interfaces import Edge, T


def create_line(edge: Edge, pos: VertexPositions):
    return Line(pos[edge.u], pos[edge.v])


def compute_angle_between_edges(edge1: Edge, edge2: Edge, pos: VertexPositions):

    assert edge1.u == edge2.u, "Assuming lines originate at same "
    "point"

    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    angle = l1.angle_between(l2)
    return N(angle)


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


def get_closest_successor(
    pos: VertexPositions, curr_edge: Edge[T], succesors: list[Edge[T]]
) -> Edge[T]:
    sedges = sorted(
        succesors, key=lambda x: compute_angle_between_edges(curr_edge, x, pos)
    )
    return sedges[0]


def add_edge_with_reference(
    pos: VertexPositions, PG: nx.PlanarEmbedding, e: Edge[T], reference: Edge[T]
):
    cw_value = is_cw(pos, e, reference)
    if cw_value:
        PG.add_half_edge_ccw(e.u, e.v, reference_neighbor=reference.v)
    else:
        PG.add_half_edge_cw(e.u, e.v, reference_neighbor=reference.v)

    return PG


def create_embedding(G: nx.Graph, pos: VertexPositions):
    edge_list = transform_graph_egdes(G)
    PG = nx.PlanarEmbedding()

    def handle_half_edge(e: Edge[T]):
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

        print(f"\n4 - before_nbs of {e.u}: {list(PG.neighbors_cw_order(e.u))}")
        reference = get_closest_successor(
            pos, e, [edge_list.get(e.u, v) for v in successors]
        )
        add_edge_with_reference(pos, PG, e, reference)
        return 4

    for e in edge_list.edges:
        val = handle_half_edge(e)
        if val == 4:
            print(
                f"edge: {e.pair}, type: {val}, curr_nbs: {list(PG.neighbors_cw_order(e.u))}"
            )

    return PG
