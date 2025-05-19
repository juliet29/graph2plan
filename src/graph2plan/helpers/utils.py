from itertools import chain, tee
from typing import Iterable

import networkx as nx


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
