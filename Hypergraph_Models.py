import numpy as np
import random
from math import comb
from itertools import combinations as combs
import Hypergraph_Functions as hf



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





###################################
#Aaron's simplicial Chung-Lu model#
###################################


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




