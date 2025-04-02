from copy import deepcopy
from graph2plan.helpers.general_interfaces import Face
from graph2plan.dual.interfaces import DualVertex, EdgeFaceDict, FacePair
from graph2plan.helpers.general_interfaces import T


import networkx as nx

from graph2plan.helpers.general_interfaces import CoordinateList, VertexPositions


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


def place_source_target_nodes(
    _G: nx.DiGraph, _pos: VertexPositions, faces: tuple[Face, Face]
):
    def handle_vertex(vertex, name, loc: tuple[float, float]):
        nx.relabel_nodes(G, {vertex: name}, copy=False)
        pos[name] = loc
        del pos[vertex]

    pos = deepcopy(_pos)
    G = deepcopy(_G)

    east_face, west_face = (
        faces  # NOTE - reversed from left/right # TODO make explicit when create the dual..
    )
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
