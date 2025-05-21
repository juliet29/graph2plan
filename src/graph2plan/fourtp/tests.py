from graph2plan.helpers.geometry_interfaces import VertexPositions
import networkx as nx
from graph2plan.dcel.original import create_embedding
from graph2plan.fourtp.faces import get_external_face
from .four_complete import check_for_shortcuts



def get_shortcuts(G: nx.Graph, pos: VertexPositions):
    PE = create_embedding(G, pos)
    outer_face = get_external_face(PE, pos)
    shortcuts = check_for_shortcuts(G, outer_face)
    return shortcuts, outer_face


