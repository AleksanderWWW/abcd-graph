import random
import Hypergraph_Functions as hf


##########Notes##########
# - Before each function is a short description, followed by an explanation of each input
# - Vertices should always be a set or a list of hashable elements.
# - Edges should always be a list of vertices.
#########################



#Get the following dictionary: num-edges -> size of giant

#V: vertices
#E: edges

def giant_component_growth(V,E):
    #We start by converting to a union-find dataset
    parents = {v : v for v in V}
    sizes = {v : 1 for v in V}
    
    #Inernal function: Finds the current root of a vertex
    def root(v):
        if parents[v] == v:
            return v
        else:
            return root(parents[v])

    #Internal function: Merges sets
    def merge(S):  
        #replace elements by their roots
        S = {root(v) for v in S}

        #If all vertices were in the same component, we don't need to merge
        if len(S) > 1:
            #When we merge, we root using the largest tree
            v = next(iter(S))
            for u in S:
                if sizes[u] > sizes[v]:
                    v = u

            #We now point all of S to v
            for u in S:
                parents[u] = v

            #Lastly, we update the size of v
            #Note: We only care about the sizes of roots, so there is no need to update the size of S\{v}
            #Note: We converted S to a set of roots, so this sum is always correct
            sizes[v] = sum([sizes[u] for u in S])

    #We shuffle E, add e in E one by one, and keep track of the size of the largest component along the way
    random.shuffle(E)
    size_of_giant = {0:1}
    counter = 0
    for e in E:
        counter += 1
        merge(e)
        size_of_giant[counter] = max(size_of_giant[counter-1],sizes[root(next(iter(e)))])
    
    return size_of_giant
                
        


 
