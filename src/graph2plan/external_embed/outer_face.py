from typing import Literal
from sympy import Polygon
import networkx as nx

from graph2plan.helpers.general_interfaces import VertexPositions



def get_outer_face_st_graph(
    PG: nx.PlanarEmbedding, pos: VertexPositions, source: Literal["v_s", "v_w"] = "v_s"
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