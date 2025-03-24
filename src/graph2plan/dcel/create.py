from os import close
import networkx as nx
import functools
from networkx import NetworkXError
from sympy import Point, Line, pi
from .interfaces import Edge, Edges
from .examples import deberg
from typing import Iterable
from icecream import ic
import colored_traceback

VertexPositions = dict[int, tuple[int, int]]


# def flip_edge(edge: tuple[int, int]):
#     a, b = edge
#     return (b, a)


def transform_graph_egdes(G: nx.Graph):
    ix=0
    all_edges = []
    for e in G.edges:
        all_edges.append(Edge(e[0], e[1], ix, 1))
        ix+=1
        all_edges.append(Edge(e[1], e[0], ix, 2))
        ix+=1

    # edges = [Edge(e[0], e[1], ix, 1) for ix, e in enumerate(G.edges)]
    # flipped_edges = [Edge(e[1], e[0], ix, 2) for ix, e in enumerate(G.edges)]

    return Edges(all_edges)


def set_difference(a: Iterable, b: Iterable):
    return list(set(a).difference(set(b)))


def create_line(edge: Edge, pos: VertexPositions):
    return Line(pos[edge.u], pos[edge.v])


# @functools.lru_cache()
def compute_angle_between_edges(edge1: Edge, edge2: Edge, pos: VertexPositions):
    assert edge1.u == edge2.u, "Assuming lines originate at same point"

    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    return l1.smallest_angle_between(l2)



def assess_cw(edge1: Edge, edge2: Edge, pos: VertexPositions):
    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    print(l1.points)


def test_cw()



def get_closest_nb(edge_list: Edges, pos: VertexPositions, vertex=3, nb=4) -> Edge | None:
    # all relevant edges..
    star = [edge for edge in edge_list.edges if edge.u == vertex]
    ref_edge = edge_list.get(vertex, nb)
    assert ref_edge

    # print(ref_edge)
    filtered_star = [e for e in star if e.v != nb]

    if not filtered_star:
        return None
    
    assert filtered_star
    assert pos

    sedges = sorted(
        filtered_star, key=lambda x: compute_angle_between_edges(ref_edge, x, pos)
    )
    return sedges[0]

def order_edges(vertex=3, nb=4):
    G, pos = deberg()
    edge_list = transform_graph_egdes(G)

    PG = nx.PlanarEmbedding()

    for e in edge_list.edges:
        if e.u not in PG.nodes and e.v not in PG.nodes: 
            print(f"u, v not yet considered {e.pair}")
            PG.add_half_edge(e.u, e.v)
        elif e.u in PG.nodes and  not list(PG.successors(e.u)):
            print(f"u {e.u} has no succesors!")
            PG.add_half_edge(e.u, e.v)
        
        else:
            closest = get_closest_nb(edge_list, pos,  e.u, e.v)
            if not closest: 
                print(f"edge: {e.u, e.v} |  None")
                PG.add_half_edge(e.u, e.v)
            else: 
                print(f"edge: {e.u, e.v} |  {closest.pair} | u succesors: {list(PG.successors(e.u))}")
                if closest.v not in PG.nodes:
                    print("closest not in PG")
                    PG.add_half_edge(e.u, e.v)
                else: 
                    PG.add_half_edge(e.u, e.v, ccw=closest.v)
                    # try: 
                    #     PG.add_half_edge(e.u, e.v, cw=closest.v)
                    # except NetworkXError:
                    #     PG.add_half_edge(e.u, e.v, ccw=closest.v)
        print(f"Updated edges: {PG.edges}\n" )
    # except NetworkXError as n:
    #     nx.draw_networkx(PG.to_directed(), pos)
    #     print(n)

    for node in PG.nodes:
        print(f"node {node}: {list(PG.neighbors_cw_order(node))}")

    return PG

                


def test():
    G, pos = deberg()
    # G.add_edges_from([(3,4), (3,1), (3,2)])
    edges = transform_graph_egdes(G)
    # print(edges.get(1,2))
    # print(edges.get(2,1))
    PG = nx.PlanarEmbedding()

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
