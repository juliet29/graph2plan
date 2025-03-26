from typing import Iterable


def set_difference(a: Iterable, b: Iterable):
    return list(set(a).difference(set(b)))
