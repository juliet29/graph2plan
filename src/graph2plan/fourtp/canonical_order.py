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
    # n: int
    n: int # number of vertices
    k: int

    # @property
    # def num_vertices(self):
    #     return len(self.vertices)

    @property
    def curr_k(self):
        return self.k
    
    def decrement_k(self):
        self.k-=1

    

    def potential_vertices(self):
        return [i for i in self.vertices.values() if i.is_potential_next and i.name != self.u and i.name != self.v]
    
    def show_vertices(self):
        s = sorted(list(self.vertices.values()), key=lambda x: (x.ordered_number, x.n_marked_nbs), reverse=True)
        pprint(s)
    


def update_neighbors_visited(G:nx.Graph, co: CanonicalOrder, vertex_name):
    nbs = G.neighbors(vertex_name)
    for nb in nbs:
        if not co.vertices[nb].is_marked:
            co.vertices[nb].n_marked_nbs +=1


def iterate_canonical_order(G:nx.Graph, co: CanonicalOrder):
    
    potential = co.potential_vertices()
    if len(potential) == 0:
        print("No potential vertices")
        return 
    if len(potential) > 1:
        print(f"Multiple potential: {[i.name for i in potential]}. Would choose {potential[0].name}")
        return 

    k = co.curr_k
    vk = potential[0]
    co.vertices[vk.name].ordered_number = k
    

    # update the visited of its neighbors.. 
    update_neighbors_visited(G, co, vk.name)

    print(f"k={k}, vk={vk.name}")
    # co.show_vertices()





    co.decrement_k()





    

def initialize_canonical_order(_G: nx.Graph):
    # TODO -> test that graph is 4TP 
    G = deepcopy(_G).to_undirected()
    vertices = {i: VertexData(i) for i in G.nodes}
    co = CanonicalOrder(vertices, u="v_s", v="v_e", w="v_w", k = G.order(), n=G.order())

    co.vertices[co.u].ordered_number = 1
    co.vertices[co.v].ordered_number = 2

    co.vertices[co.u].is_marked = True
    co.vertices[co.v].is_marked = True

    # update_neighbors_visited(G, co, co.u)
    # update_neighbors_visited(G, co, co.v) # maybe this is ok after update chords? 
    # pprint(co.show_vertices())

    # update the first node
    co.vertices[co.w].n_marked_nbs = 2
    # pprint(co.potential_vertices())

    co.show_vertices()


    iterate_canonical_order(G, co)



    # co.vertices[curr].ordered_number = co.num_vertices
    # co.vertices[curr].is_marked = True

    
    # update the visited of its neighbors.. 
    # nbs = G.neighbors(curr)
    # for nb in nbs:
    #     co.vertices[nb].n_marked_nbs +=1

    
    # update the chords of its neighbors 


    


    

