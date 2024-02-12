from itertools import combinations as combs


##########Notes##########
# - Before each function is a short description, followed by an explanation of each input
# - Vertices should always be a set or a list of hashable elements.
# - Edges should always be a list of vertices.
#########################



##########"get" functions##########
#The following functions are all data collection:
#edge_sets(V,E)
#degrees(V,E)
#volume(S,X)    X -> either dict of degrees or edges 
#subgraph(S,E)
#weak_subgraph(S,E)
#2section(V,E)
#components(V,E)
###################################


#Get a dictionary of vertex -> edges containing vertex.

#V: vertices
#E: edges

def edge_sets(V,E):
    #Initalize edge_set
    edge_sets = {v : [] for v in V}
    
    #iterate through E and update edge_sets
    for e in E:
        for v in e:
            edge_sets[v].append(e)
            
    return edge_sets


#Get a dictionary of vertex -> degree.

#V: vertices
#E: edges

def degrees(V,E):
    #Initalize degrees
    degrees = {v : 0 for v in V}

    #Update degrees by iterating through E
    for e in E:
        for v in e:
            degrees[v] = degrees[v]+1
    
    return degrees


#Get the volume (sum of degrees) of a set of vertices.

#V: subset of vertices
#X: either edges or a dictionary of degrees. The function is slower if X is a list of edges

def volume(S,X):
    #initialize volume
    volume = 0

    #get degrees if X is a list of edges
    if type(X) is list:
        #We need all vertices in the graph to call get_degrees
        V = S.copy()
        for e in X:
            V.update(e)
        X = degrees(V,X)

    #iterate through V and sum degrees
    for v in S:
        volume += X[v]

    return volume


#Get the edges in the strong induced subgraph, specified by a subset of vertices

#S: subset of vertices
#E: edges

def subgraph(S,E):
    #initialize edges
    Esub = []

    #iterate through E and add e iff e is a subset of S
    for e in E:
        if e.issubset(S):
            Esub.append(e)

    return Esub


#Get the edges in the weak induced subgraph, specified by a subset of vertices

#S: vertices
#E: edges

def weak_subgraph(S,E):
    #initialize edges
    Esub = []

    #iterate through E and add e intersect S if it has atleast one vertex
    for e in E:
        esub = e.intersection(S)
        if len(esub) > 0:
            Esub.append(esub)

    return Esub
    

#Get the connected components as a partition of vertices (list of sets)
#The graph is converted to a union-find structure for the sake of speed

#V: vertices
#E: edges

def components(V,E):

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

    #Iterate through E and merge
    for e in E:
        u = e.pop()
        v = e.pop()
        merge(u,v)

    #Build a dictionary of root -> component
    roots = {root(v) for v in V}
    components = {v : {v} for v in roots}
    for v in V:
        components[root(v)].add(v)

    return list(components.values())


#Get the edges of the 2-section graph

#E: edges

def two_section(E):
    E2sec = []
    for e in E:
        E2sec += [set(uv) for uv in list(combs(e,2))]

    #this is a convoluted but fast way to remove duplicate edges
    E2sec = list(map(set,set(map(frozenset, E2sec))))

    return E2sec            
        


##########"sort" functions##########
#The following functions are all data organization:
#sort_edges
####################################


#Get dictionary of size -> edges of that size

#E: edges

def sort_edges(E):
    #initialize partition
    edge_sizes = {len(e) for e in E}
    partition = {k : [] for k in edge_sizes}
    
    #iterate through E and update partition
    for e in E:
        partition[len(e)].append(e)
        
    return partition



 
