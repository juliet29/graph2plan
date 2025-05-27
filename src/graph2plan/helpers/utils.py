from itertools import chain, tee
from typing import Iterable
from pathlib import Path
import json

import networkx as nx

from graph2plan.constants import OUTPUTS_PATH


class NotImplementedError(Exception):
    pass


def set_difference(a: Iterable, b: Iterable):
    return list(set(a).difference(set(b)))


def set_intersection(a: Iterable, b: Iterable):
    return list(set(a).intersection(set(b)))


def pairwise(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def chain_flatten(lst: Iterable[Iterable]):
    return list(chain.from_iterable(lst))


def get_unique_items_in_list_keep_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

# TODO move to a graph utils..
def neighborhood(G, node, n):
    # TODO do something simpler if n = 1
    path_lengths = nx.single_source_dijkstra_path_length(G, node)
    return [node for node, length in path_lengths.items() if length == n]

## create a folder if it doesnt exist
# TODO share with other code bases
def get_folder_path(root_path: Path, folder_name: str):
    path_to_outputs = root_path / folder_name
    if not path_to_outputs.exists():
        try:
            path_to_outputs.mkdir()
        except:
            raise NotImplementedError

    return path_to_outputs



def write_graph(G: nx.Graph, name:str, output_path=OUTPUTS_PATH):
    G_json = nx.node_link_data(G, edges="edges")
    with open(output_path / f"{name}.json", "w+") as file:
        json.dump(G_json, default=str, fp=file)

def read_graph(name:str, output_path=OUTPUTS_PATH):
    with open(output_path / f"{name}.json", "r") as file:
        d = json.load(file)
    G: nx.Graph = nx.node_link_graph(d, edges="edges")
    return G
