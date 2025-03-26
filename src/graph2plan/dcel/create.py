import networkx as nx
from sympy import Line, Triangle, N
from .interfaces import Edge, Edges

VertexPositions = dict[int, tuple[int, int]]

# TODO move elsewhere?
def transform_graph_egdes(G: nx.Graph):
    ix = 0
    all_edges = []
    for e in G.edges:
        all_edges.append(Edge(e[0], e[1], ix, 1))
        ix += 1
        all_edges.append(Edge(e[1], e[0], ix, 2))
        ix += 1

    return Edges(all_edges)


def create_line(edge: Edge, pos: VertexPositions):
    return Line(pos[edge.u], pos[edge.v])


def compute_angle_between_edges(edge1: Edge, edge2: Edge, pos: VertexPositions):
    assert edge1.u == edge2.u, "Assuming lines originate at same "
    "point"
    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    return N(l1.smallest_angle_between(l2))


def is_cw(edge1: Edge, edge2: Edge, pos: VertexPositions):
    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    assert l2
    triangle = Triangle(*l1.points, l2.points[1])
    assert isinstance(triangle, Triangle)
    return True if triangle.area < 0 else False


def get_closest_nb(
    edge_list: Edges, pos: VertexPositions, vertex: int, nb: int
) -> Edge | None:

    star = [edge for edge in edge_list.edges if edge.u == vertex]
    filtered_star = [e for e in star if e.v != nb]
    if not filtered_star:
        return None

    ref_edge = edge_list.get(vertex, nb)
    assert ref_edge

    sedges = sorted(
        filtered_star, key=lambda x: compute_angle_between_edges(ref_edge, x, pos)
    )
    return sedges[0]


def create_embedding(G: nx.Graph, pos: VertexPositions):
    edge_list = transform_graph_egdes(G)

    PG = nx.PlanarEmbedding()

    for e in edge_list.edges:
        if e.u not in PG.nodes:
            PG.add_half_edge_first(e.u, e.v)
        elif e.u in PG.nodes and not list(PG.successors(e.u)):
            PG.add_half_edge_first(e.u, e.v)

        else:
            closest = get_closest_nb(edge_list, pos, e.u, e.v)
            if not closest:
                PG.add_half_edge_first(e.u, e.v)
            else:
                if closest.v not in PG.nodes:
                    PG.add_half_edge_first(e.u, e.v)
                else:
                    cw = is_cw(e, closest, pos)
                    if cw:
                        PG.add_half_edge_cw(e.u, e.v, reference_neighbor=closest.v)
                    else:
                        PG.add_half_edge_ccw(e.u, e.v, reference_neighbor=closest.v)

    return PG
