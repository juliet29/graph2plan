from copy import deepcopy
from dataclasses import dataclass
from typing import Union
import networkx as nx
from pprint import pprint

## TODO not really 4TP, more so prep for dual.. 

@dataclass
class VertexData:
    name: str
    ordered_number = -1
    is_marked = False
    n_marked_nbs = 0 # visited
    n_chords = 0

    def __repr__(self) -> str:
        return f"{self.name, self.ordered_number} | is_marked: {self.is_marked}, n_marked_nbs: {self.n_marked_nbs}, n_chords: {self.n_chords} "

    @property
    def is_potential_next(self):
        if not self.is_marked and self.n_marked_nbs >= 2 and self.n_chords == 0:
            print(f"{self.name} is potential next")
            return True
        return False


@dataclass
class CanonicalOrder:
    vertices: dict[str, VertexData]
    u: str
    v: str
    w: str # => v_n

    @property
    def num_vertices(self):
        return len(self.vertices)

    def potential_vertices(self):
        return [i for i in self.vertices.values() if i.is_potential_next and i.name != self.u and i.name != self.v]
    
    def show_vertices(self):
        return sorted(list(self.vertices.values()), key=lambda x: (x.ordered_number, x.n_marked_nbs), reverse=True)
    

    

def initialize_canonical_order(_G: nx.Graph):
    # TODO -> test that graph is 4TP 
    G = deepcopy(_G).to_undirected()
    vertices = {i: VertexData(i) for i in G.nodes}
    co = CanonicalOrder(vertices, u="v_s", v="v_e", w="v_w")

    co.vertices[co.u].ordered_number = 1
    co.vertices[co.v].ordered_number = 2
    pprint(co.show_vertices())

    # update the first node
    co.vertices[co.w].n_marked_nbs = 2
    pprint(co.potential_vertices())



    # co.vertices[curr].ordered_number = co.num_vertices
    # co.vertices[curr].is_marked = True

    
    # update the visited of its neighbors.. 
    # nbs = G.neighbors(curr)
    # for nb in nbs:
    #     co.vertices[nb].n_marked_nbs +=1

    
    # update the chords of its neighbors 


    


    

