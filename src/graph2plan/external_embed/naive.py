from copy import deepcopy
import networkx as nx

def embed_other_target(_PG: nx.PlanarEmbedding, vertex="v_e"):
    # TODO s
    _PG.check_structure()
    source, target = "v_s", "v_n"

    PG = deepcopy(_PG)
    ref = list(PG.neighbors_cw_order(source))[-1]
    PG.add_half_edge_cw(source, vertex, reference_neighbor=ref)
    PG.add_half_edge_first(vertex, source)
    PG.check_structure()

    ref = list(PG.neighbors_cw_order(target))[0]
    PG.add_half_edge_ccw(vertex, target, reference_neighbor=source)
    PG.add_half_edge_ccw(target, vertex, reference_neighbor=ref)
    PG.check_structure()

    directed_edges = [(source, vertex), (vertex, target)]
    return PG, directed_edges


def embed_other_source(_PG: nx.PlanarEmbedding, vertex="v_w"):
    _PG.check_structure()
    source, target = "v_s", "v_n"

    PG = deepcopy(_PG)

    ref = list(PG.neighbors_cw_order(source))[0]
    PG.add_half_edge_ccw(source, vertex, reference_neighbor=ref)
    PG.add_half_edge_first(vertex, source)
    PG.check_structure()

    ref = list(PG.neighbors_cw_order(target))[-1]
    PG.add_half_edge_cw(target, vertex, reference_neighbor=ref)
    PG.add_half_edge_cw(vertex, target, reference_neighbor=source)
    PG.check_structure()

    directed_edges = [(source, vertex), (vertex, target)]
    return PG, directed_edges


def embed_target_source_edge(_PG: nx.PlanarEmbedding, source="v_s", target="v_n"):
    PG = deepcopy(_PG)
    other_source = "v_w"
    # print(f"{source} cw: {list(PG.neighbors_cw_order(source))}")
    PG.add_half_edge_ccw(source, target, reference_neighbor=other_source)
    # print(f"{source} cw after: {list(PG.neighbors_cw_order(source))}")

    # print(f"{target} cw: {list(PG.neighbors_cw_order(target))}")
    PG.add_half_edge_cw(target, source, reference_neighbor=other_source)
    # print(f"{target} cw after: {list(PG.neighbors_cw_order(target))}")
    directed_edges = [(source, target)]

    PG.check_structure()
    return PG, directed_edges

    # check outer face, area should be opposite of if traverse other way
