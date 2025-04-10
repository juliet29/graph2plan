from copy import deepcopy
from graph2plan.helpers.general_interfaces import Face
from graph2plan.dual.interfaces import DualVertex, EdgeFaceDict, FacePair
from graph2plan.helpers.general_interfaces import T, Axis, assignments


import networkx as nx

from graph2plan.helpers.general_interfaces import CoordinateList, VertexPositions

import matplotlib.pyplot as plt

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
    # print(f"==>> vertex[0]: {vertex[0]}")
    return vertex[0]


def place_source_target_nodes(
    _G: nx.DiGraph, _pos: VertexPositions, faces: tuple[Face, Face], axis: Axis
):
    def handle_vertex(vertex, name, loc: tuple[float, float]):
        nx.relabel_nodes(G, {vertex: name}, copy=False)
        pos[name] = loc
        del pos[vertex]

    pos = deepcopy(_pos)
    G = deepcopy(_G)

    if axis == "y":
        east_face, west_face = (
            faces  # NOTE - reversed from left/right # TODO make explicit when create the dual..
        )
        coords = CoordinateList.to_coordinate_list(_pos)
        west_vertex = get_node_by_face(_G, west_face)
        east_vertex = get_node_by_face(_G, east_face)
        # print(f"==>> west_vertex: {west_vertex}")
        # print(f"==>> east_vertex: {east_vertex}")

        delta = 1
        # print(coords.bounds)

        handle_vertex(west_vertex, "w*", (coords.bounds.min_x - delta, coords.mid_values.y ))
        handle_vertex(east_vertex, "e*", (coords.bounds.max_x + delta, coords.mid_values.y ))
    else:
        south_face, north_face = (
            faces
        )
        # north_face, south_face = (
        #     faces
        # )
        coords = CoordinateList.to_coordinate_list(_pos)
        south_vertex = get_node_by_face(_G, south_face)
        north_vertex = get_node_by_face(_G, north_face)
        # print(f"==>> south_vertex: {south_vertex}")
        # print(f"==>> north_vertex: {north_vertex}")

        delta = 1
        # print(coords.bounds)

        handle_vertex(south_vertex, "s*", (coords.mid_values.x, coords.bounds.min_y - delta ))
        handle_vertex(north_vertex, "n*", (coords.mid_values.x , coords.bounds.max_y + delta ))


    return G, pos


def create_dual(
    edge_face_dict: EdgeFaceDict[str], init_graph_pos: VertexPositions[str], axis: Axis = "y"
):
    
    def init_vertex(dual_vertex: DualVertex) -> str:
        
        ix = len(G.nodes)+1
        name = dual_vertex.name(ix)
        pos[name] = dual_vertex.face.get_position(init_graph_pos)
        G.add_node(
            name,
            face=dual_vertex.face,
            edge=dual_vertex.edge,
            side=dual_vertex.side,
        )
        # print(f"initializing vertex! name: {name}, face: {dual_vertex.face}")
        return name

    def get_or_init_vertex(dual_vertex: DualVertex) -> str:
        try:
            matching_vertices = [
                vertex
                for vertex, data in G.nodes(data=True)
                if data.get("face") == dual_vertex.face
            ]
        except Exception:
            print(G.nodes(data=True))
            raise Exception

        if not matching_vertices:
            return init_vertex(dual_vertex)

        assert len(matching_vertices) == 1, (
            f"Should only have one matching vertex, instead have: {matching_vertices}"
        )
        return matching_vertices[0]

    G = nx.DiGraph()
    pos: VertexPositions = {}
    assn = assignments[axis]
    # face_ix = 0
    source, target = assn.source, assn.target

    for edge, face_pair in edge_face_dict.items():
        f1 = get_or_init_vertex(DualVertex(face_pair.left, edge, "LEFT"))

        f2 = get_or_init_vertex(DualVertex(face_pair.right, edge, "RIGHT"))

        if axis == "y":
            if frozenset(edge) == frozenset((source, target)):
                G.add_edge(f2, f1)
            else:
                G.add_edge(f1, f2)
        else:
            if frozenset(edge) == frozenset((source, target)):
                G.add_edge(f1, f2)
            else:
                G.add_edge(f2, f1)


        

    G, pos = place_source_target_nodes(G, pos, edge_face_dict[source, target], axis)
    plt.figure()
    nx.draw_networkx(G, pos)

    return G, pos
