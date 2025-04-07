from typing import Literal
from sympy import Polygon
import networkx as nx
from itertools import cycle
from graph2plan.helpers.general_interfaces import VertexPositions

SourceVertex = Literal["v_s", "v_w"]
TargetVertex = Literal["v_n", "v_e"]


def get_outer_face_st_graph(
    PG: nx.PlanarEmbedding, pos: VertexPositions, source:SourceVertex = "v_s"
):
    def get_polygon_area(face: list):
        p = Polygon(*[pos[i] for i in face])
        assert isinstance(p, Polygon)
        return p.area

    PG.check_structure()
    source_neighbors = list(PG.neighbors_cw_order(source))
    ccw_edge = (source, source_neighbors[-1])
    outer_face = PG.traverse_face(*ccw_edge)

    # check using area
    inner_face = PG.traverse_face(ccw_edge[1], ccw_edge[0])
    outer_area, inner_area = [get_polygon_area(i) for i in (outer_face, inner_face)]
    if inner_area < 1:
        assert outer_area > 1
    else:
        assert outer_area < 1

    return outer_face


def split_outer_face(outer_face:list, source: SourceVertex="v_s", target: TargetVertex = "v_n" ):
    def create_nbs(pair):
        nbs = []
        cnt = 0
        check = False
        i1, i2 = pair
        for i in cycle(outer_face):
            if i == i1:
                check = True
            if check:
                nbs.append(i)
                if i == i2:
                    check = False
                    print(nbs)
                    break
            cnt+=1
            if cnt > len(outer_face*2):
                print(nbs)
                break
        return nbs
    
    assert source in outer_face and target in outer_face
    other_source_nbs = create_nbs((target, source))
    other_target_nbs = create_nbs((source, target))
    return other_source_nbs, other_target_nbs