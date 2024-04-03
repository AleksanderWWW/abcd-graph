import numpy as np
import random

def CM(d):
    l = []
    for v in d.keys():
        l.extend([v]*d[v])
    random.shuffle(l)
    E = [[l[2*i],l[2*i+1]] for i in range(int(np.floor(sum(d.values())/2)))]
    return E

def build_degrees(n,gamma,delta,zeta):
    Delta = int(np.floor(n**zeta))
    avail = list(range(delta,Delta+1))
    p = []
    norm = sum(x**(-gamma) for x in avail)
    for x in avail:
        p.append((x**(-gamma))/norm)
    degrees = list(reversed(sorted(np.random.choice(avail,size=n,p=p))))
    if sum(degrees)%2 == 1:
        degrees[0] += 1
    return degrees

def build_community_sizes(n,beta,s,tau):
    S = int(np.floor(n**tau))
    avail = list(range(s,S+1))
    p = []
    norm = sum(y**(-beta) for y in avail)
    for y in avail:
        p.append((y**(-beta))/norm)
    big_list = np.random.choice(avail,size=int(np.ceil(n/s)),p=p)
    community_sizes = []
    index = 0
    while sum(community_sizes) < n:
        community_sizes.append(big_list[index])
        index += 1
    excess = sum(community_sizes)-n
    if excess > 0:
        if (community_sizes[-1]-excess) >= s:
            community_sizes[-1] -= excess
        else:
            removed = community_sizes[-1]
            community_sizes = community_sizes[:-1]
            for i in range(removed-excess):
                community_sizes[i] += 1
    community_sizes = list(reversed(sorted(community_sizes)))
    return community_sizes

def build_C(community_sizes):
    C = {}
    v_last = -1
    for i,c in enumerate(community_sizes):
        C[i] = [v for v in range(v_last+1,v_last+1+c)]
        v_last += c
    return C

def build_deg(degrees,C,community_sizes,xi):
    phi = 1-sum(c**2 for c in community_sizes)/(n**2)
    deg = {}
    avail = []
    lock = 0
    d_previous = degrees[0]+1
    for d in degrees:
        if (d<d_previous) and (lock < len(community_sizes)):
            threshold = d*(1-xi*phi)+1
            while community_sizes[lock] >= threshold:
                avail.extend(C[lock])
                lock += 1             
                if lock == len(community_sizes):
                    break
        v = avail.pop(np.random.choice(len(avail)))
        deg[v] = d
        d_previous=d
    return deg

def split_deg(deg,C):
    def rand_round(x):
        p = x-np.floor(x)
        if random.uniform(0,1) <= p:
            return int(np.floor(x)+1)
        else:
            return int(np.floor(x))
    deg_c = {v:rand_round((1-xi)*deg[v]) for v in deg.keys()}
    for community in C.values():
        if sum(deg_c[v] for v in community)%2 == 1:
            v_max = deg_c[community[0]]
            for v in community:
                if deg_c[v] > deg_c[v_max]:
                    v_max = v
            deg_c[v_max] += 1
            if deg_c[v_max] > deg[v_max]:
                deg_c[v_max] -= 2
    deg_b = {v:(deg[v]-deg_c[v]) for v in deg.keys()}
    return deg_c,deg_b

def build_E_c(deg_c,C):
    E_c = []
    for community in C.values():
        E_c.extend(CM({v:deg_c[v] for v in community}))
    return E_c

def build_E_b(deg_b):
    return CM(deg_b)

#n: number of vertices
#gamma: power-law parameter for degrees, between 2 and 3
#delta: min degree
#zeta: parameter for max degree, between 0 and 1
#beta: power-law parameter for community sizes, between 1 and 2
#s: min community size
#tau: parameter for max community size, between zeta and 1
#xi: noise parameter, between 0 and 1
def ABCD(n,gamma,delta,zeta,beta,s,tau,xi):
    degrees = build_degrees(n,gamma,delta,zeta)
    community_sizes = build_community_sizes(n,beta,s,tau)
    C = build_C(community_sizes)
    deg = build_deg(degrees,C,community_sizes,xi)
    deg_c,deg_b = split_deg(deg,C)
    E_c = build_E_c(deg_c,C)
    E_b = build_E_b(deg_b)
    return E_c,E_b