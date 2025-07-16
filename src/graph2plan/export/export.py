from copy import deepcopy
from sysconfig import get_path

from networkx import relabel_nodes
import reprit
from graph2plan.fourtp.tests import test_degen_cycle
from graph2plan.helpers.graph_interfaces import CardinalDirectionEnum, get_vertex_name, mapping_for_exterior_vertices
from graph2plan.helpers.utils import chain_flatten, get_folder_path, read_pickle, write_pickle
from graph2plan.dual.interfaces import Domains
from graph2plan.constants import OUTPUTS_PATH
import networkx as nx
from itertools import combinations
import json
from graph2plan.rel.rel2 import STGraphs, write_graph
from rich import print as rprint 

# def merged_domains_to_floorplan(domains: Domains):
#     domains.write_floorplan(OUTPUTS_PATH) # TODO how to test this?


# def save_rel_graphs(T1: nx.DiGraph, T2: nx.DiGraph):
#     def save_G(G: nx.DiGraph, name):
#         G_json = nx.node_link_data(G, edges="edges")

#         with open(OUTPUTS_PATH / f"{name}.json", "w+") as file:
#             json.dump(G_json, default=str, fp=file)

#     save_G(T1, "T1")
#     save_G(T2, "T2")


# def read_rel_graphs():
#     def read_G(name):
#         with open(OUTPUTS_PATH / f"{name}.json", "r") as file:
#             d = json.load(file)
#         G: nx.DiGraph = nx.node_link_graph(d, edges="edges")
#         return G

#     return STGraphs(read_G("T1"), read_G("T2"))


def generate_connectivities(st_graphs: STGraphs):
    # TODO write test for three-cycle graphs => should have four..
    def get_paths(G: nx.DiGraph, source, target):
        return [i for i in nx.all_simple_edge_paths(G, source, target)]
    
    def create_graph_from_path_combo(path_combo:list[int]):
        G = nx.Graph()
        for key in path_combo:
            path = all_paths[key]
            G.add_edges_from(path)

        return G
    

    T1, T2 = deepcopy(st_graphs)
    relabel_nodes(T1, mapping_for_exterior_vertices(), copy=False)
    relabel_nodes(T2, mapping_for_exterior_vertices(), copy=False)
    # replace name in graph...
    print(T1.edges)
    print(T2.edges)



    T1_source_and_target = (CardinalDirectionEnum.SOUTH.name, CardinalDirectionEnum.NORTH.name)  # TODO encode in graph /
    T2_source_and_target = (CardinalDirectionEnum.WEST.name, CardinalDirectionEnum.EAST.name)

    # T1_source_and_target = (get_vertex_name(CardinalDirectionEnum.SOUTH), get_vertex_name(CardinalDirectionEnum.NORTH))  # TODO encode in graph /
    # T2_source_and_target = (get_vertex_name(CardinalDirectionEnum.WEST), get_vertex_name(CardinalDirectionEnum.EAST))

    # T1_get_path = get_paths(T1, *T1_source_and_target)
    # T2_get_path = get_paths(T2, *T2_source_and_target)

    all_paths = chain_flatten(
        [
            get_paths(G, *nodes)
            for G, nodes in zip([T1, T2], (T1_source_and_target, T2_source_and_target))
        ]
    )
    rprint(f"all paths: {all_paths}")
    all_paths = {(ix + 1): path for ix, path in enumerate(all_paths)}


    all_combinations = []
    for key in all_paths.keys():
        combos = [i for i in combinations(all_paths.keys(), key)]
        all_combinations.extend(combos)

    

        if key > 4:
            print("Key is > 4.. breaking")
            break

    
    rprint(f"all combos: {all_combinations}")

    
    connectivity_graphs = [create_graph_from_path_combo(path_combo) for path_combo in all_combinations]
    assert len(connectivity_graphs) == len(all_combinations)



    # map paths and combinations, create graphs

    return connectivity_graphs



# TODO better way of orgranizing intermmediate stuff.. -> general reading + writing @ each stage? w names attatched..


# def test_generate_connectivites():
#     # T1, T2 = read_rel_graphs()
#     return generate_connectivities(STGraphs.read_rel_graphs())


def save_case_and_connectivities(case_name: str, domains: Domains, st_graphs: STGraphs):
    folder_path = get_folder_path(OUTPUTS_PATH, case_name)
    # save floorpan 
    domains.write_floorplan(folder_path)
    # save st graphs 
    st_graphs.save_rel_graphs(folder_path)
    # save connectivity graphs in a folder.. 
    connectivity_folder_path = get_folder_path(folder_path, "connectivity")
    connectivity_graphs = generate_connectivities(st_graphs)
    rprint(connectivity_graphs)
    for ix, graph in enumerate(connectivity_graphs):
        write_graph(graph, f"_{ix:02}", connectivity_folder_path)

    # print(f"Finished saving results for {case_name}")

    # 

if __name__ == "__main__":
    print("Running export test")
    # merged_doms, T1, T2 = test_degen_cycle()
    # write_pickle([merged_doms, T1, T2 ], "test_degen_cycle_results_250508")
    merged_doms, T1, T2 = read_pickle("test_degen_cycle_results_250508")
    save_case_and_connectivities("three_plan", merged_doms, STGraphs(T1, T2))

    




## NEXT -> for this case, create folder with plan, T1, T2, and all the graphs..
## maybe for plan2eplus, need to think about what is the core functionality, and then experiments are on top of that.. -> so define a narrow api.. dont try to define the experimenr structure...
