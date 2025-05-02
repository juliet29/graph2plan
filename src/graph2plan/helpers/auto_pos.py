from graph2plan.helpers.geometry_interfaces import Coordinate, VertexPositions
from .geometry_interfaces import T
from copy import deepcopy


def assign_cardinal_pos(
    arrs: list[list[T]], _pos: dict, delta_x: int, delta_y:int
):
    max_len = max([len(i) for i in arrs])
    n_arrs = len(arrs)

    pos = deepcopy(_pos)
    default_y = n_arrs / 2
    default_x = max_len / 2
    init_x = init_y = 0

    pos["v_w"] = Coordinate(init_x, default_y)
    pos["v_e"] = Coordinate(max_len + delta_x + 1, default_y)

    pos["v_s"] = Coordinate(default_x, init_y)
    pos["v_n"] = Coordinate(default_x, n_arrs + delta_y)
    return pos


def assign_pos(arrs: list[list[T]],  shift_value=1, ASSIGN_CARDINAL=False) -> VertexPositions:

    pos = {}
    delta_x = delta_y = 1

    if ASSIGN_CARDINAL:
        pos = assign_cardinal_pos(arrs, pos, delta_x, delta_y)

    for level, arr in enumerate(arrs):
        shift = shift_value if level % 2 else 0
        for ix, vertex in enumerate(arr):
            x = ix + delta_x + shift
            y = level + delta_y
            pos[vertex] = Coordinate(x, y)

    return VertexPositions({k: v.pair for k, v in pos.items()})
