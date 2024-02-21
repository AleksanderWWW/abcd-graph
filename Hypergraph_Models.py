#test
import numpy as np
import random
from math import comb
from itertools import combinations as combs
import Hypergraph_Functions as hf
import time



##########Notes##########
# - Before each function is a short description, followed by an explanation of each input
# - Vertices should always be a set or a list of hashable elements.
# - Edges should always be a list of vertices.
# - The functions only return hyperedges, not vertices
#########################



##########Models##########
#The following models are currently available:
#erdos_renyi
#chung_lu
#configuration_model
##########################


#Generates the edges of an Erdos-Renyi hypergraph

#V: Either a set of vertices or the number of vertices
#m: Either a list of edges or a list [m_1,m_2,...,m_k] where m_i is the number of i-edges

def erdos_renyi(V,m):
    #If V is a number, we convert to a list
    if type(V) is int:
        V = list(range(V))
    #We convert V to a list so that we can use np.random.choice
    else:
        V = list(V)

    #If m is a list of edges, we get the number of edges of each size
    if (type(m[0]) is set) or (type(m[0]) is list):
        #sort edges by size
        edge_dict = hf.sort_edges(m)

        #convert m to a list of num edges per size
        sizes = edge_dict.keys()       
        m = [0]*max(sizes)
        for k in sizes:
            m[k-1] = len(edge_dict[k])

    #Initialize edges
    E_by_size = {}
    E = []

    #Iterate through edge sizes and build edges
    for k in range(1,len(m)+1):
        if m[k-1] > 0:
            #If we are to generate more than 50% of edges of a given size, we instead build non-edges
            remove = False
            if m[k-1] > comb(len(V),k)/2:
                remove = True
                m[k-1] = comb(len(V),k) - m[k-1]

            #Initialize edges of size k
            E_by_size[k] = set()
            #loop until we have enough edges built
            while(len(E_by_size[k]) < m[k-1]):
                #By storing a set of frozensets, we throw away duplicate edges
                new_edge = frozenset(np.random.choice(V,k,replace = False))
                E_by_size[k].add(new_edge)
            
            #Here we flip edges to non-edges if needed
            if remove:
                E_by_size[k] = {frozenset(e) for e in combs(V,k)} - E_by_size[k]

            #Finally, we convert back to a list of sets and add to E
            E_by_size[k] = list(map(set, list(E_by_size[k])))
            E += E_by_size[k]

    return E


#Generates the edges of a Chung-Lu hypergraph

#V: Either a set of vertices or a number of vertices
#m: Either a list of edges or a list of num edges per size
#degrees: Either a list or a dictionary of degrees.

#Note: Acceptable inputs are
# - vertices and edges (V,E)
# - vertices, num edges per size, and degree dict (V,m,degree dict)
# - int, num edges per size, and degree list (n,m,degree list)

def chung_lu(V,m,degrees = None):
    #If V is a number, we convert to a list
    if type(V) is int:
        V = list(range(V))
    else:
        V = list(V)

    #If m is a list of edges, we get the degrees and the number of edges of each size
    if (type(m[0]) is set) or (type(m[0]) is list):
        degrees = hf.degrees(V,m)
        
        #sort edges by size
        edge_dict = hf.sort_edges(m)

        #convert m to a list of num edges per size
        sizes = edge_dict.keys()
        m = [0]*max(sizes)
        for k in sizes:
            m[k-1] = len(edge_dict[k])

    #If degrees is a list, we convert to a dictionary
    #Note: If V was given as a set, and degrees as a list of degrees, then the degrees might get shuffled
    if type(degrees) is list:
        degrees = dict(zip(V,degrees))
    L = hf.volume(V,degrees)
    
    #choices is a dictionary with degrees[v] keys pointing to v
    #I've tested, and this is much faster than making a list 
    choices = dict.fromkeys(set(range(L)))
    counter = 0
    current_vertex = 0
    #We need L keys in total
    while (counter<L):
        for i in range(degrees[V[current_vertex]]):
            choices[counter] = V[current_vertex]
            counter += 1
        current_vertex += 1

    #E is the set of edges to be returned
    E = []
    for k in range(len(m)):
        #Adding all edges of size k+1
        for i in range(m[k]):
            e = []
            for j in range(k+1):
                e.append(choices[random.randint(0,L-1)])
            E.append(e)
    return E


#Generates the edges of a configuration model

#V: Either a set of vertices or a number of vertices
#m: Either a list of edges or a list of num edges per size
#degrees: Either a list or a dictionary of degrees.

#Note: Acceptable inputs are
# - vertices and edges (V,E)
# - vertices, num edges per size, and degree dict (V,m,degree dict)
# - int, num edges per size, and degree list (n,m,degree list)

def configuration_model(V,m,degrees = None):
    #If V is a number, we convert to a list
    if type(V) is int:
        V = list(range(V))
    else:
        V = list(V)

    #If m is a list of edges, we get the degrees and the number of edges of each size
    if (type(m[0]) is set) or (type(m[0]) is list):
        degrees = hf.degrees(V,m)
        
        #sort edges by size
        edge_dict = hf.sort_edges(m)

        #convert m to a list of num edges per size
        sizes = edge_dict.keys()       
        m = [0]*max(sizes)
        for k in sizes:
            m[k-1] = len(edge_dict[k])

    #If degrees is a list, we convert to a dictionary
    #Note: If V was given as a set, and degrees as a list of degrees, then the degrees might get shuffled
    if type(degrees) is list:
        degrees = dict(zip(V,degrees))
    L = hf.volume(V,degrees)
    
    #choices is a list with degrees[v] copies of v for each v in V
    choices = []
    counter = 0
    current_vertex = 0
    #We need L keys in total
    while (counter<L):
        for i in range(degrees[V[current_vertex]]):
            choices.append(V[current_vertex])
            counter += 1
        current_vertex += 1
    
    #E is the set of edges to be returned
    E = []
    #We shuffle choices and pop elements one by one
    random.shuffle(choices)
    for k in range(len(m)):
        #Adding all edges of size k+1
        for i in range(m[k]):
            e = []
            for j in range(k+1):
                e.append(choices.pop())
            E.append(e)

    return E


################
###ABCD Model###
################


def ABCD(n,gamma,delta,zeta,beta,s,tau,xi,rewire=True):

    start_time = time.time()
    #Fixing input parameters
    #I might add an initial check to make sure parameters are fiesable
    if type(n) is not int:
        n = len(n)
    V = set(range(n))
    if type(zeta) is int:
        max_degree = zeta
    else:
        max_degree = int(np.floor(n**zeta))
    if type(tau) is int:
        max_size = tau
    else:    
        max_size = int(np.floor(n**tau))

    #Phase 1: creating a degree distribution
    #The degree distribution is a truncated power-law with parameter gamma and truncation delta/max_degree
    available_degrees = list(range(delta,max_degree+1))
    degree_distribution = []
    normalization = sum(d**(-gamma) for d in available_degrees)
    for d in available_degrees:
        degree_distribution.append((d**(-gamma))/normalization)
    degree_sequence = sorted(np.random.choice(available_degrees,n,p=degree_distribution))
    #If the degree is odd, we add 1 to the max degree
    if sum(degree_sequence)%2 == 1:
        degree_sequence[-1] = degree_sequence[-1]+1

    #Phase 2: creating a community size distribution
    available_sizes = list(range(s,max_size+1))
    size_distribution = []
    normalization = sum(c**(-beta) for c in available_sizes)
    for c in available_sizes:
        size_distribution.append((c**(-beta))/normalization)
    #We generate community sizes until the total is >= n
    #Since np.random.choice is slow if called many times, we get a big list and then truncate
    #The number of communities cannot exceed n/s, so we generate that many
    temp_sequence = list(np.random.choice(available_sizes,int(np.ceil(n/s)),p=size_distribution))
    size_sequence = []
    sum_of_sizes = 0
    while(sum_of_sizes < n):
        new_size = temp_sequence.pop()
        size_sequence.append(new_size)
        sum_of_sizes += new_size
    overflow = sum_of_sizes - n
    if overflow > 0:
        #If overflow > 0 and the last size added is at least s+overflow, we subtract overflow from this size
        if new_size >= (s+overflow):
            size_sequence[-1] -= overflow
        #Otherwise, we delete this community and add 1 to communities at random until the sum is n
        else:
            size_sequence.pop()
            random.shuffle(size_sequence)
            for i in range(new_size - overflow):
                size_sequence[i] += 1
    size_sequence = sorted(size_sequence)
    num_communities = len(size_sequence)
    #Lastly, we partition the vertices into communities
    #At first, communities will be a dict of label -> vertices
    #Later, this will be changed to label -> vertices and edges
    communities = {C : set() for C in range(num_communities)}
    current_vertex = 0
    #We can now partition the vertices into communities
    for C in communities.keys():
        for i in range(size_sequence[C]):
            communities[C].add(current_vertex)
            current_vertex += 1
    
    #Phase 3: assigning degrees to nodes
    #Starting from the largest degree, we lock some communities if they are too small,
    #then choose a random unlocked vertex and give it the current degree
    degrees = {}
    #Read the ABCD paper to understand phi better
    #It's an error term that controls background edges that happen to land in a community
    phi = 1 - np.sum(np.array([c**2 for c in size_sequence]))/n**2
    #When we unlock a community, we add all of its vertices to available_vertices
    #When we assign a degree to a vertex, we remove it from available_vertices
    available_vertices = []
    #lock determines which communities are off limits when assigning a degree
    lock = num_communities
    #We iterate through degrees, from largest to smallest
    for d in reversed(degree_sequence):
        #A degree can only be assigned to a vertex in C if |C| >= min_size
        #Read the ABCD paper to understand this lowerbound
        min_size = d*(1-xi*phi)+1
        locked_sizes = size_sequence[0:lock].copy()
        #We iterate through locked_sizes, find all sizes that are now available, and update new_lock accordingly
        new_lock = lock
        for c in reversed(locked_sizes):
            if c<min_size:
                break
            new_lock -= 1
        #range(new_lock,lock) are the newly available communities
        for C in range(new_lock,lock):
            available_vertices.extend(communities[C])
        #We assign d to a random vertex in available_vertices
        #We use pop to also remove the vertex from availbale_vertices
        degrees[available_vertices.pop(random.randrange(len(available_vertices)))] = d
        lock = new_lock
    
    #Phases 4&5: creating edges and rewiring
    #We define a rounding function which preserves expectation
    def rand_round(x):
        p = x-np.floor(x)
        if random.uniform(0,1) <= p:
            return int(np.floor(x)+1)
        else:
            return int(np.floor(x))
    #We now split degrees into community_degrees and background_degrees
    community_degrees = dict.fromkeys(V)
    for v in V:
        community_degrees[v] = rand_round((1-xi)*degrees[v])
    #We check each community for an odd volume
    #If yes, we add 1 to a max degree node
    for C in communities.keys():
        C_degrees = {v : community_degrees[v] for v in communities[C]}
        vol_C = sum(C_degrees.values())
        if vol_C%2 == 1:
            v_max = max(C_degrees, key=C_degrees.get)
            community_degrees[v_max] += 1
            #If xi is small enough, it's possible that the community degree becomes too large
            #So we check for this and subtract 1 instead if that's the case
            if community_degrees[v_max] > degrees[v_max]:
                community_degrees[v_max] -= 2
    #Now we build background_degrees, which is just the remainer for each vertex
    background_degrees = {v : degrees[v]-community_degrees[v] for v in V}
    #Before building graphs, we will define a function that quickly finds multi-edges
    #In most cases, we will have a small set containing all edges that could potentially be multi-edges
    #From here until the end of the code, I flip between sets, frozensets, and lists seemingly at random
    #This is because I'm bad at coding
    def find_dupes(X,look_list = 'all'):
        if look_list == 'all':
            X_frozen = [frozenset(sorted(e)) for e in X if len(set(e))==2]
        else:
            X_frozen = [frozenset(sorted(e)) for e in X if (set(e) in look_list and len(set(e)) == 2)]
        S = set()
        dupes = []
        for e in X_frozen:
            if e in S:
                dupes.append(set(e))
            else:
                S.add(e)
        return dupes
            
    #We can now build all of the community graphs, and the background graph, as configuration models
    #If rewire=True, we rewire communities as we build. Otherwise, we leave loops and multi-edges in
    E = []
    for C in communities.keys():
        community_dict = {v : community_degrees[v] for v in communities[C]}
        community_edges = configuration_model(community_dict.keys(),[0,int(sum(community_dict.values())/2)],community_dict)
        #Life is easier when edges are sorted
        community_edges = [sorted(e) for e in community_edges]
        if rewire:
            #We build recycle_list containing all loops and multi-edges
            #recycle_list -> edges that will be rewired
            #dupes -> set(e) for all e contributing to a multi-edge
            #dupes_found -> updates as we iterate through community_edges
            #The first time we find a dupe, we keep it and add the edge to dupes_found
            #Then, every other time we see that edge, we add it to recycle_list
            recycle_list = []
            dupes = find_dupes(community_edges)
            dupes_found = []
            for e in community_edges:
                if len(set(e)) == 1:           
                    recycle_list.append(e)
                elif set(e) in dupes:
                    if set(e) in dupes_found:
                        recycle_list.append(e)
                    else:
                        dupes_found.append(set(e))
            #Now we rewrire all of recycle_list and repeat until recycle_list is either empty or doesn't decrease in size
            while len(recycle_list) > 0:
                #As we rewire, we keep track of the new edges built
                #These new edges are the only ones that can lead to further issues
                look_list = []
                e_index = -1
                for e in recycle_list:
                    e_index += 1
                    if e != 'skip':                        
                        f = random.choice([x for x in community_edges if x != e])                        
                        #If we happen to pick another edge in recycle_list, we mark it and skip it in the loop
                        #We only need to label `skip' if f is later in the list than e
                        if f in recycle_list[e_index:]:
                            #This is convoluted nonsense and should be ignored
                            recycle_list[recycle_list[e_index:].index(f)+e_index] = 'skip'                        
                        community_edges.remove(e)
                        community_edges.remove(f)
                        community_edges.append(sorted([e[0],f[0]]))
                        community_edges.append(sorted([e[1],f[1]]))                       
                        look_list.append({e[0],f[0]})
                        look_list.append({e[1],f[1]})
                #After rewiring, we make new_recycle_list in the same way
                new_recycle_list = []
                #We now specify look_list to speed up the dupe finding process
                dupes = find_dupes(community_edges,look_list)
                dupes_found = []
                for e in community_edges:
                    if set(e) in look_list:
                        if len(set(e)) == 1:
                            new_recycle_list.append(e)
                        elif set(e) in dupes:
                            if set(e) in dupes_found:
                                new_recycle_list.append(e)
                            else:
                                dupes_found.append(set(e))
                    #If the number of bad edges does not go down, we give up and move the issue to the background graph
                if len(new_recycle_list) >= len(recycle_list):
                    for e in new_recycle_list:
                        community_edges.remove(e)
                        v1 = e.pop()
                        v2 = e.pop()
                        community_degrees[v1] -= 1
                        community_degrees[v2] -= 1
                        background_degrees[v1] += 1
                        background_degrees[v2] += 1
                    break
                recycle_list = new_recycle_list
        E.extend(community_edges)
        communities[C] = {'vertices':communities[C],'edges':community_edges}
    #Finally, we handle the background graph
    background_edges = configuration_model(V,[0,round(sum(background_degrees.values())/2)],background_degrees)
    #Again, this is a temporary fix to an issue with configuration_model
    background_edges = [sorted(e) for e in background_edges if len(e)>0]
    if rewire:
        #We do the same process as we did for each community, except that we don't give up when rewiring
        recycle_list = []
        #We have to deal with a new type of bad edge: e that is already in a community graph
        community_collisions = []
        for e in background_edges:
            if len(set(e))==2:
                #Because we sorted edges, we don't have to worry about list ordering when checking if e in E
                if e in E:
                    community_collisions.append(set(e))
        dupes = find_dupes(background_edges)
        dupes_found = []
        #Now we build recycle_list
        for e in background_edges:
            if len(set(e)) == 1:
                recycle_list.append(e)
            elif set(e) in community_collisions:
                recycle_list.append(e)
            elif set(e) in dupes:
                if set(e) in dupes_found:
                    recycle_list.append(e)
                else:
                    dupes_found.append(set(e))
        #Now we rewrire all of recycle_list and repeat until recycle_list is empty
        while len(recycle_list) > 0:
            look_list = []
            e_index = -1
            for e in recycle_list:
                e_index += 1
                if e != 'skip':
                    f = random.choice([x for x in background_edges if x != e])
                    if f in recycle_list[e_index:]:
                        #This is convoluted nonsense and should be ignored
                        recycle_list[recycle_list[e_index:].index(f)+e_index] = 'skip'
                    background_edges.remove(e)
                    background_edges.remove(f)
                    background_edges.append(sorted([e[0],f[0]]))
                    background_edges.append(sorted([e[1],f[1]]))                       
                    look_list.append({e[0],f[0]})
                    look_list.append({e[1],f[1]})
            #After rewiring, we make new_recycle_list in the same way
            recycle_list = []
            community_collisions = []
            for e in background_edges:
                if set(e) in look_list:
                    if len(set(e))==2:
                        #Because we sorted edges, we don't have to worry about list ordering when checking if e in E
                        if e in E:
                            community_collisions.append(set(e))
            dupes = find_dupes(background_edges,look_list)
            dupes_found = []
            #Now we build recycle_list
            for e in background_edges:
                if set(e) in look_list:
                    if len(set(e)) == 1:
                        recycle_list.append(e)
                    elif set(e) in community_collisions:
                        recycle_list.append(e)
                    elif set(e) in dupes:
                        if set(e) in dupes_found:
                            recycle_list.append(e)
                        else:
                            dupes_found.append(set(e))
    E.extend(background_edges)
    communities['Background Graph'] = {'vertices':V,'edges':background_edges}
    
    end_time = time.time()
    print('run time = {0} seconds'.format(np.round(end_time-start_time)))

    return V,E,communities



#######################################
###Aaron's simplicial Chung-Lu model###
#######################################


# Makes a single hyperedge of size k according to soft Chung-Lu with weights p.
# CHECKED BASIC FUNCTION
def make_CL_edge(V,k,p):
    return(np.random.choice(V,size=k,p=p))


# Computes alpha, as in Example 5.1 of Overleaf. Note that at this point k is "fixed" and so is not included as an index where it is not needed.
# CHECKED BASIC FUNCTION
def get_alpha(Theta,beta,V,k,eps = (0.1)**10):
    # Compute gamma
    gamma = np.zeros(V)
    for edge in Theta:
        for v in np.unique(edge): # Computing probabilities, so we don't want to deal with self-loops.
            gamma[v] = gamma[v] + 1 # Doing raw counts.
    for v in range(V):
        gamma[v] = gamma[v]/len(Theta) # normalize
        
    # Compute alpha
    alpha = np.zeros(V)
    for v in range(V):
        alpha[v] = (1 - beta[v,k]*(1-gamma[v]))/(eps + gamma[v]) # Include small "eps" value to reduce numerical issues at cost of small bias.
    return(alpha)


# Does the simple upweight 
# CHECKED BASIC FUNCTION
def simple_upweight(Theta,p,V,alpha,beta,k):
    m = len(Theta)

    S = Theta[np.random.randint(m)] # Choose a random hyperedge to "be inside"
    adj_p = np.zeros(V)
    for v in range(V):
        if v in S:
            adj_p[v] = p[v,k]*alpha[v]
        else:
            adj_p[v] = p[v,k]*beta[v,k]
    tot = sum(adj_p)
    for v in range(V):
        adj_p[v] = adj_p[v]/tot
    return(adj_p)


# Preprocesses p into a matrix of the appropriate size/shape.
# CHECKED BASIC FUNCTION
def Proc_p(p,K_max):
    if len(p.shape) == 2:
        return(p)
    if len(p.shape) == 1:
        V = p.shape[0]
        p = np.tile(p, K_max).reshape(K_max,V).transpose()
        return(p)
    return(-1) # error


# Preprocesses beta into a matrix of the appropriate size/shape.
# CHECKED BASIC FUNCTION
def Proc_beta(beta,V,K_max):
    res = np.zeros((V,K_max))
    if type(beta) is float:
        res.fill(beta)
        return(res)
    if len(beta.shape) == 2:
        return(beta)
    if len(beta.shape) == 1:
        if beta.shape[0] == V:
            beta = np.tile(beta, K_max).reshape(K_max,V).transpose()
            return(beta)
        if beta.shape[0] == K_max:
            beta = np.tile(beta, V).reshape(V,K_max)
            return(beta)
    return(-1) # error


# Create a graph according to Algorithm 2 in our Overleaf.

# V: integer - number of vertices.
# n: nd array of integers of length K_max, with n[k] being the number of hyperedges of size k+2. 
# p: ndarray of height V and width K_max, with p[v,k] being the weight of vertex v for hypergraphs of size k. If an array of length V is passed, it should be copied K_max times to make an array.
# beta: ndarray of height V and width K_max, with beta[v,k] being the weighting scheme seen in Example 5.1. If an array of length V or K_max is passed, it should be copied to make the 2d array. If a number is passed, it should be copied to make the array.
# Global (default = None): if not None, should be a list of integers of length K_max, with Global[k] saying how often to add the set "all vertices" to $\Theta_{k}$. If an integer is passed, it should be copied K_max times to make a list.

def Soft_CL(V,n,p,beta,Global=None,eps = (0.1)**10):
    # Preprocessing to make sure everything is the right shape.
    K_max = n.shape[0]
    p = Proc_p(p,K_max)
    beta = Proc_beta(beta,V,K_max)

    # Initialize
    H_list = [] # Elements will be the hyperedges (set objects)
    
    for k in range(K_max-1,-1,-1): # loop over size of hyperedge, from biggest to smallest
        # Freeze the hyperedge list, as the algorithm does
        Theta = H_list.copy()
        if k == (K_max-1): # In this case the list is empty, so add the "global" background. Note I'm wasting computational time doing this, since I don't need to compute alpha here. Oh well.
            Theta.append(np.array([x for x in range(V)]))
        if Global is not None:
            for i in range(Global[k]): # OK, this is surely a silly way to do this. Oh well.
                Theta.append(np.array([x for x in range(V)]))
        alpha = get_alpha(Theta,beta,V,k,eps=eps) # Compute alpha.
        for ind in range(n[k]): # make n[k] hyperedges
            adj_p = simple_upweight(Theta,p,V,alpha,beta,k) # Choose an element of theta, adjust p.
            H_list.append(make_CL_edge(V,k+2,adj_p))
    return(H_list)




