import numpy as np
import random
from math import comb
from itertools import combinations as combs
import Hypergraph_Functions as hf
import Hypergraph_Models as hm



##########Notes##########
# - Before each function is a short description, followed by an explanation of each input
# - Vertices should always be a set or a list of hashable elements.
# - Edges should always be a list of vertices.
#########################



##########Landry Stuff##########
#These three functions are all from "The simpliciality of higher order networks"
#simplicial_fraction
#edit_simpliciality
#face_edit_simpliciality
################################


#Get the simplicial fraction of a hypergraph
#The simplicial fraction is the fraction of edges (of size at least 3) that satisfy downward closure

#V: vertices
#E: edges

def simplicial_fraction(V,E):
    #They ignore 1-edges in their paper, so we throw away 1-edges here
    E = [set(e) for e in E if len(e) > 1]
    edge_sets = hf.edge_sets(V,E)

    #For each edge, we add 1 to bottom and add 1 to top if the edge is a simplicial complex
    top = 0
    bottom = 0
    for e in E:
        #In their paper, the only check edges of size at least 3
        if len(e) > 2:
            bottom += 1
            #relevant_edges are edges containing v for each v in e
            relevant_edges = set()
            for v in e:
                relevant_edges = relevant_edges.union([frozenset(sorted(edge)) for edge in edge_sets[v]])
            #po_set is the simplicial closure of e. We don't include sets of size 0 or 1, nor do we include e
            po_set = set()
            for k in range(2,len(e)):
                po_set = po_set.union([frozenset(sorted(edge)) for edge in combs(e,k)])

            #Check if e is a simplicial complex
            if (po_set <= relevant_edges):
                top += 1
                
    return top/bottom
            

#Get the edit simpliciality of a hypergraph
#The edit simpliciality is |E|/|C| where C is the smallest simplicial complex containing E

#V: vertices
#E: edges

def edit_simpliciality(V,E):
    #They ignore 1-edges in their paper, so we throw away 1-edges here
    E = [set(e) for e in E if len(e) > 1]    

    #Finding the set of maximal edges of size at least 3
    E_check = [e for e in E if len(e) > 2]
    edge_sets = hf.edge_sets(V,E_check)
    #We build a dictionary of e -> T/F
    is_max = {frozenset(sorted(e)) : True for e in E_check}
    for e in E_check:
        #Some edges will point to false before they are hit in the loop
        if is_max[frozenset(sorted(e))]:
            #Any edge containing e will contain v for all v in e
            #Hence, we find v in e with the fewest edges to check for edges containing e
            v = next(iter(e))
            for u in e:
                if len(edge_sets[u]) < len(edge_sets[v]):
                    v = u
            #For each edge, we check containment in both directions and update accordingly
            for edge in edge_sets[v]:
                if set(e) < set(edge):
                    is_max[frozenset(sorted(e))] == False
                    break
                elif set(edge) < set(e):
                    is_max[frozenset(sorted(edge))] == False
            
    E_max = [e for e in E_check if is_max[frozenset(sorted(e))]]

    #C is the set of edges in the simplicial closure.
    #We start by adding all 2-edges, then add all PoSets of maximal edges
    C = {frozenset(sorted(e)) for e in E if len(e) == 2}
    for e in E_max:
        for k in range(2,len(e)+1):
            C = C.union({frozenset(sorted(edge)) for edge in combs(e,k)})

    return len(E)/len(C)
     

#Get the face edit simpliciality of a hypergraph
#The face edit simpliciality is the average edit simpliciality across the maximal edges

#V: vertices
#E: edges

def face_edit_simpliciality(V,E):
    #They ignore 1-edges in their paper, so we throw away 1-edges here
    E = [set(e) for e in E if len(e) > 1]    

    #Finding the set of maximal edges of size at least 3
    E_check = [e for e in E if len(e) > 2]
    edge_sets = hf.edge_sets(V,E_check)
    #We build a dictionary of e -> T/F
    is_max = {frozenset(sorted(e)) : True for e in E_check}
    for e in E_check:
        #Some edges will point to false before they are hit in the loop
        if is_max[frozenset(sorted(e))]:
            #Any edge containing e will contain v for all v in e
            #Hence, we find v in e with the fewest edges to check for edges containing e
            v = next(iter(e))
            for u in e:
                if len(edge_sets[u]) < len(edge_sets[v]):
                    v = u
            #For each edge, we check containment in both directions and update accordingly
            for edge in edge_sets[v]:
                if set(e) < set(edge):
                    is_max[frozenset(sorted(e))] == False
                    break
                elif set(edge) < set(e):
                    is_max[frozenset(sorted(edge))] == False
            
    E_max = [e for e in E_check if is_max[frozenset(sorted(e))]]

    #We iterate over E_max and compute the edit simpliciality of each maximal face
    FES = 0
    #We now need edge_sets for all edges
    edge_sets = hf.edge_sets(V,E)

    #We loop through E_max and compute the edit simpliciality for each edge
    for e in E_max:
        #C_face is the simplicial closure of e
        C_face = {frozenset(sorted(e))}
        for k in range(2,len(e)):
            C_face = C_face.union({frozenset(sorted(edge)) for edge in combs(e,k)})
        #Before computing E_face, we restrict to only edges containing v for each v in e
        relevant_edges = {frozenset(sorted(e))}
        for v in e:
            relevant_edges = relevant_edges.union({frozenset(sorted(edge)) for edge in edge_sets[v]})
        #E_face is the set of edges in C_face that are also in the graph
        E_face = C_face.intersection(relevant_edges)
        FES += len(E_face)/len(C_face)
        
    FES = FES/len(E_max)
    return FES



##########Current stuff##########
#These are all functions relevant to our current work
#simplicial_pairs
#simplicial_matrix
#################################


#Get the matrix that counts simplicial pairs

#V: vertices
#E: edges

def simplicial_pairs(V,E):
    #Convert to set and list of sets
    V = set(V)
    E = [set(e) for e in E]
    
    #Getting relevant data
    edge_sets = hf.edge_sets(V,E)
    degrees = {v : len(edge_sets[v]) for v in V}
    max_size = max({len(e) for e in E})

    #M is the matrix of pairs
    M = np.zeros((max_size,max_size))

    #We iterate through E and compute the number of pairs with e as the smaller edge
    for e in E:
        #Any edge f containing e will contain v for all v in e
        #Thus, we find v with the smallest degree for our search
        v = list(e)[0]
        for u in e:
            if degrees[u] < degrees[v]:
                v = u
        #Now we check for f containing e
        for f in edge_sets[v]:
            #As far as I know, e<f returns false almost immediately if len(e)>=len(f)
            #If I ever learn that this isn't the case, I will throw away all such f before hand
            if e<f:
                M[len(e)-1][len(f)-1] += 1
            
    return M

                
#Get the simplicial_matrix of a graph
#The simplicial matrix is the cell-wise ratio of simplicial pairs between a real graph and a re-sampling
        
#V: vertices
#E: edges
#samples: the number of times we re-sample, set to 1 by default
#model: the synthetic model used for the re-sampling, set to 'CL' by default

#Note: the available models at this time are
#       'CL' -> Chung-Lu
#       'ER' -> Erdos-Renyi
#       'CM' -> Configuration model

def simplicial_matrix(V,E,samples = 1,model = 'CL'):
    #We first get the matrix of simplicial pairs
    M_top = simplicial_pairs(V,E) + 1/samples

    #Next, we get the same matrix for the re-sample, depending on the model specified
    if model == 'ER':
        E_resampled = hm.erdos_renyi(V,E)
        M_bottom = simplicial_pairs(V,E_resampled)
        for i in range(samples-1):
            E_resampled = hm.erdos_renyi(V,E)
            M_bottom = np.add(M_bottom, simplicial_pairs(V,E_resampled))
    elif model == 'CM':
        E_resampled = hm.configuration_model(V,E)
        M_bottom = simplicial_pairs(V,E_resampled)
        for i in range(samples-1):
            E_resampled = hm.configuration_model(V,E)
            M_bottom = np.add(M_bottom, simplicial_pairs(V,E_resampled))
    else:
        E_resampled = hm.chung_lu(V,E)
        M_bottom = simplicial_pairs(V,E_resampled)
        for i in range(samples-1):
            E_resampled = hm.chung_lu(V,E)
            M_bottom = np.add(M_bottom, simplicial_pairs(V,E_resampled))
    M_bottom = (M_bottom + 1)/samples
    
    return M_top/M_bottom
   
