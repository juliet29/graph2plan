import networkx as nx
from networkx import NetworkXError
from sympy import Line, Triangle, N
from .interfaces import Edge, Edges, T


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
    # print(f"edge in create line: {edge}")
    return Line(pos[edge.u], pos[edge.v])


def compute_angle_between_edges(edge1: Edge, edge2: Edge, pos: VertexPositions):
    assert edge1.u == edge2.u, "Assuming lines originate at same "
    "point"
    
    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    return N(l1.smallest_angle_between(l2))


def is_cw(pos: VertexPositions, edge1: Edge, edge2: Edge):
    # print(f"edge1 in is_cw: {edge1}")
    # print(f"edge2 in is_cw: {edge2}")
    l1, l2 = [create_line(e, pos) for e in [edge1, edge2]]
    assert l1
    assert l2
    if l1.is_parallel(l2):
        base = l1.points[0]
        other = l2.points[1]
        return True if base.compare(other) == 1 else False
    triangle = Triangle(*l1.points, l2.points[1])
    try:
        assert isinstance(triangle, Triangle)
    except AssertionError:
        print(f"triangle: {triangle}\nl1: {l1}\nl2: {l2}")
        raise Exception

    return True if triangle.area < 0 else False



def get_closest_successor(pos: VertexPositions, curr_edge: Edge[T], succesors:list[Edge[T]] 
) -> Edge[T]:
    sedges = sorted(
        succesors, key=lambda x: compute_angle_between_edges(curr_edge, x, pos)
    )
    return sedges[0]

def add_edge_with_reference(pos: VertexPositions, PG: nx.PlanarEmbedding, e:Edge[T], reference:Edge[T]):
    # print(f"ref in add edge w ref {reference}")
    cw_value = is_cw(pos, e, reference)
    if cw_value:
        PG.add_half_edge_cw(e.u, e.v, reference_neighbor=reference.v)
    else:
        PG.add_half_edge_ccw(e.u, e.v, reference_neighbor=reference.v)

    return PG


def create_embedding_simple(G: nx.Graph, pos: VertexPositions):
    edge_list = transform_graph_egdes(G)
    PG = nx.PlanarEmbedding()

    def handle_half_edge(e:Edge[T]):
        if e.u not in PG.nodes:
            PG.add_half_edge_first(e.u, e.v)
            return 1

        successors:list[T] = list(PG.successors(e.u))
        

        if not successors:
            PG.add_half_edge_first(e.u, e.v)
            return 2
        
        if len(successors) == 1:
            ref = edge_list.get(e.u, successors[0])

            add_edge_with_reference(pos, PG, e, ref)
            return 3
        
        reference = get_closest_successor(pos, e, [edge_list.get(e.u,v) for v in successors])
        add_edge_with_reference(pos, PG, e, reference)
        return 4
    
    for e in edge_list.edges:
        val = handle_half_edge(e)
        print(f"edge: {e.pair}, type: {val}, curr_nodes: {PG.nodes}")

    return PG

    


        







# def create_embedding(G: nx.Graph, pos: VertexPositions):
#     edge_list = transform_graph_egdes(G)
#     PG = nx.PlanarEmbedding()

#     for e in edge_list.edges:
#         if e.u not in PG.nodes:
#             PG.add_half_edge_first(e.u, e.v)
#         elif e.u in PG.nodes and not list(PG.successors(e.u)):
#             PG.add_half_edge_first(e.u, e.v)

#         else:
#             closest = get_closest_successor(edge_list, pos, e.u, e.v)
#             if not closest: # better check has only 1 nb.. 
#                 PG.add_half_edge_first(e.u, e.v)
#             else:
#                 if closest.v not in PG.nodes:
#                     PG.add_half_edge_first(e.u, e.v)
#                 elif closest.v not in list(PG.successors(e.u)):
#                     print(f"NB not in succes.. curr: {e.pair}, closest: {closest.pair}\ncurr succesors: {list(PG.successors(e.u))}")
#                     PG.add_half_edge_first(e.u, e.v)
#                 else: # TODO split this.. 
#                     cw = is_cw(e, closest, pos)
#                     try:
#                         if cw:
#                             PG.add_half_edge_ccw(e.u, e.v, reference_neighbor=closest.v)
#                         else:
#                             PG.add_half_edge_ccw(e.u, e.v, reference_neighbor=closest.v)
#                     except NetworkXError:
#                         print(f"curr: {e.pair}, closest: {closest.pair}\ncurr succesors: {list(PG.successors(e.u))}")
#                         raise Exception

#     return PG
