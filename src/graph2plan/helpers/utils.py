from itertools import tee
from typing import Iterable


def set_difference(a: Iterable, b: Iterable):
    return list(set(a).difference(set(b)))


def pairwise(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
