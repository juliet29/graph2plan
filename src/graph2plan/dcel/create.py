from os import close
import networkx as nx
import functools
from networkx import NetworkXError
from sympy import Point, Line, pi
from .interfaces import Edge, Edges
from .examples import deberg
from typing import Iterable
from icecream import ic


VertexPositions = dict[int, tuple[int, int]]


def flip_edge(edge: tuple[int, int]):
    a, b = edge
    return (b, a)


def transform_graph_egdes(G: nx.Graph):
    edges = [Edge(e[0], e[1], ix, 1) for ix, e in enumerate(G.edges)]
    flipped_edges = [Edge(e[1], e[0], ix, 2) for ix, e in enumerate(G.edges)]

    return Edges(edges + flipped_edges)


def set_difference(a: Iterable, b: Iterable):
    return list(set(a).difference(set(b)))


# @functools.lru_cache()
def compute_angle_between_edges(edge1: Edge, edge2: Edge, pos: VertexPositions):
    print(edge1, edge2)

    def create_line(edge: Edge):
        return Line(pos[edge.u], pos[edge.v])

    if edge1.u == edge2.u:
        l1, l2 = [create_line(e) for e in [edge1, edge2]]

        assert l1

        return l1.angle_between(l2)


def create_embedding(G: nx.Graph):

    def add_half_edges(vertex: int):
        nbs: list[int] = list(nx.neighbors(G, vertex))
        if len(nbs) == 1:
            print(f"1 nb only - edge is ({vertex, nbs[0]})")
            if (vertex, nbs[0]) in marked_edges:
                return
            PG.add_half_edge(vertex, nbs[0])  # e11
            marked_edges.append((vertex, nbs[0]))
            return

        for nb in nbs:
            if (vertex, nb) in marked_edges:
                return
            angles = []
            other_nbs = set_difference(nbs, [nb])
            print(f"curr edge{(vertex, nb)}. other nbs: {other_nbs}")

            if len(other_nbs) == 1:
                print(f"2 nb only - edge is ({vertex, nb})")

                try:
                    PG.add_half_edge(vertex, nb, cw=other_nbs[0])
                except NetworkXError:
                    PG.add_half_edge(vertex, nb)
                marked_edges.append((vertex, nb))
                return
            for ix, other in enumerate(other_nbs):

                angle = compute_angle_between_edges(
                    edges.get(vertex, nb), edges.get(vertex, other), pos
                )
                angles.append(angle)
            ix_of_smallest = angles.index(min(angles))
            closest_nb = other_nbs[ix_of_smallest]
            print(f"closest nb of {(vertex, nb)} is {closest_nb}")
            try:
                PG.add_half_edge(vertex, nb, cw=closest_nb)
            except NetworkXError:
                PG.add_half_edge(vertex, nb)

            marked_edges.append((vertex, nb))
            return

    PG = nx.PlanarEmbedding()
    G, pos = deberg()
    edges = transform_graph_egdes(G)
    # iterate over nodes..

    marked_edges = []

    for edge in edges.edges:
        if (edge.u, edge.v) not in marked_edges:
            print(f"\ncandidate edge {(edge.u, edge.v) }")
            add_half_edges(edge.u)
        print(f"marked edges: {marked_edges}")

    return PG


def order_edges(vertex=3, nb=4):
    G, pos = deberg()
    # G.add_edges_from([(3,4), (3,1), (3,2)])
    edge_list = transform_graph_egdes(G)

    # all relevant edges..
    star = [edge for edge in edge_list.edges if edge.u == vertex]
    print(star)
    ref_edge = edge_list.get(vertex, nb)
    print(ref_edge)
    filtered_star = [e for e in star if e.v != nb]

    # for edge in star:
    #     angle_rad = compute_angle_between_edges(ref_edge, edge, pos)
    #     print(f"angle btwn {ref_edge.pair}  and {edge.pair} == {angle_rad}")

    sedges = sorted(
        filtered_star, key=lambda x: compute_angle_between_edges(ref_edge, x, pos)
    )
    return sedges[0]


def test():
    G, pos = deberg()
    # G.add_edges_from([(3,4), (3,1), (3,2)])
    edges = transform_graph_egdes(G)
    # print(edges.get(1,2))
    # print(edges.get(2,1))

    angle_rad = compute_angle_between_edges(edges.get(3, 4), edges.get(3, 1), pos)
    print(angle_rad)
    angle_rad2 = compute_angle_between_edges(edges.get(3, 4), edges.get(3, 2), pos)
    print(angle_rad2)

    print(angle_rad2 > angle_rad)  # type: ignore
    min([angle_rad, angle_rad2])
    # print(f"Angle between vectors (in radians): {angle_rad}")
    # print(f"Angle between vectors (in degrees): {angle_deg}")

    # angle_deg = np.degrees(angle_rad)

    # print(f"The angle between the vectors is: {angle_rad:.2f} radians ({angle_deg:.2f} degrees)")
