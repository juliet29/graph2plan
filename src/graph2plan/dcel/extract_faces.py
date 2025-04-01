from ast import Name
from collections import namedtuple
from copy import deepcopy
from attr import frozen
import networkx as nx

from networkx import NetworkXException
from pprint import pprint

# TODO these should become helpers interfaces
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
from itertools import cycle
from functools import partial

from graph2plan.dual.interfaces import FacePair, MarkedNb
from graph2plan.dual.interfaces import EdgeFaceDict
from graph2plan.dual.interfaces import DualVertex
from graph2plan.dual.interfaces import VertexDomain
from graph2plan.helpers.utils import pairwise




def prep_dual(
    PG: nx.PlanarEmbedding, directed_edges: list[tuple[T, T]]
) -> EdgeFaceDict[T]:
    edge_face_dict: EdgeFaceDict = {}
    for e in directed_edges:
        v, w = e
        right_face = PG.traverse_face(v, w)
        left_face = PG.traverse_face(w, v)
        edge_face_dict[(v, w)] = FacePair(Face(left_face), Face(right_face))
    return edge_face_dict


def get_node_by_face(G: nx.DiGraph, face: Face):
    vertex = [vertex for vertex, data in G.nodes(data=True) if data.get("face") == face]
    assert len(vertex) == 1
    print(f"==>> vertex[0]: {vertex[0]}")
    return vertex[0]



def place_source_target_nodes(_G:nx.DiGraph, _pos: VertexPositions, faces:tuple[Face, Face]):

    def handle_vertex(vertex, name, loc:tuple[float, float]):
        nx.relabel_nodes(G, {vertex: name}, copy=False)
        pos[name] = loc
        del pos[vertex]

    pos = deepcopy(_pos)
    G = deepcopy(_G)

    east_face, west_face= faces # NOTE - reversed from left/right # TODO make explicit when create the dual.. 
    coords = CoordinateList.to_coordinate_list(_pos)
    west_vertex = get_node_by_face(_G, west_face)
    east_vertex = get_node_by_face(_G, east_face)
    delta = 1


    handle_vertex(west_vertex, "w*", (coords.bounds.min_x - delta, coords.mid_values.y))
    handle_vertex(east_vertex, "e*", (coords.bounds.max_x + delta, coords.mid_values.y))

    return G, pos 




def create_dual(
    edge_face_dict: EdgeFaceDict[str], init_graph_pos: VertexPositions[str]
):
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

    for edge, face_pair in edge_face_dict.items():
        f1 = get_or_init_vertex(DualVertex(face_ix, face_pair.left, edge, "LEFT"))

        f2 = get_or_init_vertex(DualVertex(face_ix + 1, face_pair.right, edge, "RIGHT"))

        if frozenset(edge) == frozenset((source, target)):
            G.add_edge(f2, f1)
        else:
            G.add_edge(f1, f2)

        face_ix += 1

    G, pos = place_source_target_nodes(G, pos, edge_face_dict[source, target])
    nx.draw_networkx(G, pos)

    return G, pos


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
