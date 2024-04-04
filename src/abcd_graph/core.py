from typing import TypeAlias

import numpy as np
import random

from abcd_graph.utils import rand_round, powerlaw_distribution

COMMUNITIES: TypeAlias = dict[int, list[int]]


def configuration_model(degree_sequence: dict) -> list[list[int]]:
    l = []
    for v in degree_sequence.keys():
        l.extend([v]*degree_sequence[v])
    random.shuffle(l)
    E = [[l[2*i], l[2*i+1]] for i in range(int(np.floor(sum(degree_sequence.values())/2)))]
    return E


def build_degrees(n: int, gamma: float, delta: int, zeta: float) -> list[int]:
    max_degree = int(np.floor(n**zeta))
    avail = list(range(delta, max_degree+1))

    probabilities = powerlaw_distribution(avail, gamma)

    degrees = list(reversed(sorted(np.random.choice(avail, size=n, p=probabilities))))
    if sum(degrees) % 2 == 1:
        degrees[0] += 1
    return degrees


def build_community_sizes(n: int, beta: float, s: int, tau: float) -> list[int]:
    max_community_size = int(np.floor(n**tau))
    max_community_number = int(np.ceil(n/s))
    avail = list(range(s, max_community_size + 1))

    probabilities = powerlaw_distribution(avail, beta)

    big_list = np.random.choice(avail, size=max_community_number, p=probabilities)
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


def build_communities(community_sizes: list[int]) -> COMMUNITIES:
    communities = {}
    v_last = -1
    for i, c in enumerate(community_sizes):
        communities[i] = [v for v in range(v_last+1, v_last+1+c)]
        v_last += c
    return communities


def assign_degrees(
        degrees: list[int], communities: COMMUNITIES, community_sizes: list[int], xi: float,
) -> dict[int, int]:
    phi = 1-sum(c**2 for c in community_sizes)/(len(degrees)**2)
    deg = {}
    avail = []
    lock = 0
    d_previous = degrees[0]+1
    for d in degrees:
        if (d < d_previous) and (lock < len(community_sizes)):
            threshold = d*(1-xi*phi)+1
            while community_sizes[lock] >= threshold:
                avail.extend(communities[lock])
                lock += 1
                if lock == len(community_sizes):
                    break
        v = avail.pop(np.random.choice(len(avail)))
        deg[v] = d
        d_previous = d
    return deg


# TODO: naming degree list vs degree sequence (as dict)
def split_degrees(degrees: dict[int, int], communities: COMMUNITIES, xi: float):
    deg_c = {v: rand_round((1-xi)*degrees[v]) for v in degrees.keys()}
    for community in communities.values():
        if sum(deg_c[v] for v in community) % 2 == 1:
            v_max = deg_c[community[0]]
            for v in community:
                if deg_c[v] > deg_c[v_max]:
                    v_max = v
            deg_c[v_max] += 1
            if deg_c[v_max] > degrees[v_max]:
                deg_c[v_max] -= 2
    deg_b = {v: (degrees[v]-deg_c[v]) for v in degrees.keys()}
    return deg_c, deg_b


def build_community_edges(community_degrees: dict[int, int], communities: COMMUNITIES) -> list[list]:
    community_edges = []
    for community in communities.values():
        community_edges.extend(configuration_model({v: community_degrees[v] for v in community}))
    return community_edges


def build_background_edges(background_degrees: dict[int, int]) -> list[list]:
    return configuration_model(background_degrees)
