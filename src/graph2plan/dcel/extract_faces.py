from ast import Name
from collections import namedtuple
from attr import frozen
import networkx as nx
from typing import Generic, Literal, NamedTuple, TypeVar

from networkx import NetworkXException
from pprint import pprint
from graph2plan.dcel.interfaces import (
    T,
    Coordinate,
    Edge,
    Edges,
    Face,
    CoordinateList,
    VertexPositions,
)
from random import uniform
from itertools import cycle, tee
from functools import partial

# from graph2plan.dual.check import check_num_faces_is_correct


# def extract_faces(PG: nx.PlanarEmbedding):
#     """[Based on networkx source code](https://networkx.org/documentation/stable/_modules/networkx/algorithms/planarity.html#PlanarEmbedding.check_structure)"""

#     counted_half_edges = set()
#     num_faces = 0
#     num_half_edges = 0
#     faces = {}
#     for v in PG.nodes:
#         for w in PG.neighbors_cw_order(v):
#             num_half_edges += 1
#             if (v, w) not in counted_half_edges:
#                 # We encountered a new face
#                 num_faces += 1
#                 # Mark all half-edges belonging to this face
#                 face = PG.traverse_face(v, w, counted_half_edges)
#                 faces[num_faces] = face
#                 # print(f"==>> face: {face}")
#     check_num_faces_is_correct(len(PG.nodes), num_half_edges, num_faces)
#     print(num_faces)
#     return faces


# TODO check out using e.next_face_half_edge..
# def extract_faces(PG: nx.PlanarEmbedding):


class FacePair(Generic[T], NamedTuple):
    left: Face[T]
    right: Face[T]


EdgeFaceDict = dict[tuple[T, T], FacePair[T]]


def prep_dual(
    PG: nx.PlanarEmbedding, directed_edges: list[tuple[T, T]]
) -> EdgeFaceDict[T]:
    # edges  = Edges([Edge(*i) for  i in list(PG.edges)])
    # unique_edges = edges.find_unique()
    edge_face_dict: EdgeFaceDict = {}
    for e in directed_edges:
        v, w = e
        right_face = PG.traverse_face(v, w)
        left_face = PG.traverse_face(w, v)
        edge_face_dict[(v, w)] = FacePair(Face(left_face), Face(right_face))
    return edge_face_dict


class DualVertex(NamedTuple, Generic[T]):
    ix: int
    face: Face
    edge: tuple[T, T]
    side: Literal["LEFT", "RIGHT"]

    @property
    def name(self):
        return f"v_f{self.ix}"


def get_node_by_face(G: nx.DiGraph, face: Face):
    vertex = [vertex for vertex, data in G.nodes(data=True) if data.get("face") == face]
    assert len(vertex) == 1
    print(f"==>> vertex[0]: {vertex[0]}")
    return vertex[0]


def create_dual(
    edge_face_dict: EdgeFaceDict[str], init_graph_pos: VertexPositions[str]
):
    def finish():
        # TODO use get_node_by_face()
        west_vertex = [
            vertex
            for vertex, data in G.nodes(data=True)
            if data.get("face") == west_face
        ]
        assert len(west_vertex) == 1
        west_vertex = west_vertex[0]
        print(f"==>> west_vertex: {west_vertex}")
        east_vertex = [
            vertex
            for vertex, data in G.nodes(data=True)
            if data.get("face") == east_face
        ]
        assert len(east_vertex) == 1
        east_vertex = east_vertex[0]
        print(f"==>> east_vertex: {east_vertex}")

        coords = CoordinateList.to_coordinate_list(pos)
        delta = 1
        v = west_vertex
        name = "w*"
        nx.relabel_nodes(G, {v: name}, copy=False)
        pos[name] = (coords.bounds.min_x - delta, coords.mid_values.y)
        del pos[v]
        v = east_vertex
        name = "e*"
        nx.relabel_nodes(G, {v: name}, copy=False)
        pos[name] = (coords.bounds.max_x + delta, coords.mid_values.y)
        del pos[v]

    def init_vertex(dual_vertex: DualVertex) -> str:
        pos[dual_vertex.name] = dual_vertex.face.get_position(init_graph_pos)
        G.add_node(
            dual_vertex.name,
            face=dual_vertex.face,
            edge=dual_vertex.edge,
            side=dual_vertex.side,
        )
        return dual_vertex.name

    def get_or_init_vertex(dual_vertex: DualVertex) -> str:
        matching_vertices = [
            vertex
            for vertex, data in G.nodes(data=True)
            if data.get("face") == dual_vertex.face
        ]

        if not matching_vertices:
            return init_vertex(dual_vertex)

        assert len(matching_vertices) == 1, (
            f"Should only have one matching vertex, instead have: {matching_vertices}"
        )
        return matching_vertices[0]

    G = nx.DiGraph()
    pos: VertexPositions = {}
    face_ix = 0
    source = "v_s"
    target = "v_n"
    key_edge = frozenset((source, target))

    # todo could be other way..
    east_face, west_face = edge_face_dict[source, target]

    for edge, face_pair in edge_face_dict.items():
        f1 = get_or_init_vertex(DualVertex(face_ix, face_pair.left, edge, "LEFT"))

        f2 = get_or_init_vertex(DualVertex(face_ix + 1, face_pair.right, edge, "RIGHT"))

        if frozenset(edge) == key_edge:
            G.add_edge(f2, f1)
        else:
            G.add_edge(f1, f2)

        face_ix += 1

        # print(seen_edges)

    finish()
    nx.draw_networkx(G, pos)

    return G, pos


def check_is_source_target_graph(G: nx.DiGraph, show=False):
    sources = [x for x in G.nodes() if G.in_degree(x) == 0]
    targets = [x for x in G.nodes() if G.out_degree(x) == 0]
    assert len(sources) == 1 and len(targets) == 1
    # further, check that all nodes are touched o n paths from s to t..
    if show:
        print(f"==>> sources: {sources}")
        print(f"==>> targets: {targets}")


MarkedNb = NamedTuple("MarkedNb", [("name", str), ("mark", Literal["IN", "OUT"])])


def pairwise(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def find_vertex_faces(PG: nx.PlanarEmbedding, directed_edges: list[tuple], node):
    dpg = PG.to_directed().edge_subgraph(directed_edges)
    cw_neighbors = list(PG.neighbors_cw_order(node))
    incoming = list(dpg.predecessors(node))  # type: ignore
    outgoing = list(dpg.successors(node))  # type: ignore

    marked_cw_nbs = []
    for nb in cw_neighbors:
        if nb in incoming:
            marked_cw_nbs.append(MarkedNb(nb, "IN"))
        elif nb in outgoing:
            marked_cw_nbs.append(MarkedNb(nb, "OUT"))
        else:
            raise Exception("should be in incoming or outgoing")
    # print(f"==>> marked_cw_nbs: {marked_cw_nbs}")

    nb_cycle = cycle(marked_cw_nbs)
    count = 0

    incoming_face_edge, outgoing_face_edge = None, None
    left_face, right_face = None, None

    for a, b in pairwise(nb_cycle):
        # print(f"==>> a,b: {a,b}")
        count += 1
        if not incoming_face_edge and a.mark == "IN" and b.mark == "OUT":
            incoming_face_edge = sorted([a, b], key=lambda x: x.mark)
            continue

        if not outgoing_face_edge and a.mark == "OUT" and b.mark == "IN":
            outgoing_face_edge = sorted([a, b], key=lambda x: x.mark)
            continue

        if incoming_face_edge and outgoing_face_edge:
            left_face = Face(PG.traverse_face(node, incoming_face_edge[0].name))
            right_face = Face(PG.traverse_face(outgoing_face_edge[0].name, node))
            break

        if count > len(marked_cw_nbs) * 2:
            raise Exception(
                f"Can't find incoming and outgoing for {node} -> {incoming}, {outgoing}"
            )

    assert left_face and right_face
    return left_face, right_face


def get_longest_path_length(G, source, target):
    path_lengths = [len(x) for x in nx.all_simple_paths(G, source, target)]

    sorted_paths = sorted(path_lengths, reverse=True)
    return sorted_paths[0]


class VertexDomain(NamedTuple):
    x_min: int
    x_max: int


def calculate_x_domains(
    dual_graph: nx.DiGraph, PG: nx.PlanarEmbedding, directed_edges: list[tuple]
):
    source = "w*"
    target = "e*"
    d1 = partial(get_longest_path_length, dual_graph, source)
    D1 = d1(target)
    print(f"==>> D1: {D1}")

    vertex_distances: dict[str, VertexDomain] = {}

    for node in PG.nodes:
        if node == "v_s" or node == "v_n":
            continue
        left_face, right_face = find_vertex_faces(PG, directed_edges, node)
        v_left = get_node_by_face(dual_graph, left_face)
        v_right = get_node_by_face(dual_graph, right_face)
        vertex_distances[node] = VertexDomain(d1(v_left), d1(v_right))
    print(f"==>> vertex_distances: {vertex_distances}")

    return vertex_distances
