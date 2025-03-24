import networkx as nx
import numpy as np
from .interfaces import Edge
from .examples import deberg


VertexPositions = dict[int, tuple[int, int]]

def flip_edge(edge:tuple[int, int]):
    a, b = edge
    return (b, a)


def compute_angle_between_edge(edge1: Edge, edge2: Edge, pos:VertexPositions):
    def create_vector(edge: Edge):
        return np.array([pos[edge.u], pos[edge.v]])
    
    v1, v2 = (create_vector(e) for e in [edge1, edge2])

    print(v1)
    print(v2)

    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    return angle_rad, angle_deg

def test():
    G, pos = deberg()
    edges = [Edge(e[0], e[1], ix, 1) for ix, e in enumerate(G.edges)]
    angle_rad, angle_deg = compute_angle_between_edge(edges[0], edges[1], pos)
    print(angle_rad)
    print(f"Angle between vectors (in radians): {angle_rad}")
    print(f"Angle between vectors (in degrees): {angle_deg}")
    
    # angle_deg = np.degrees(angle_rad)
    
    # print(f"The angle between the vectors is: {angle_rad:.2f} radians ({angle_deg:.2f} degrees)")