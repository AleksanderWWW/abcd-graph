# Copyright (c) 2024 Jordan Barrett
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__all__ = [
    "build_degrees",
    "build_community_sizes",
    "build_communities",
    "assign_degrees",
    "split_degrees",
    "configuration_model",
    "build_recycle_list",
    "rewire_edge",
    "push_to_background",
    "rewire",
    "build_community_edges",
    "add_background_edges",
]

import numpy as np
from numpy.typing import NDArray
from typing_extensions import TypeAlias

from abcd_graph.utils import (
    powerlaw_distribution,
    rand_round,
)

COMMUNITIES: TypeAlias = dict[int, list[int]]
DEGREE_LIST: TypeAlias = NDArray[np.int64]
DEGREE_SEQUENCE: TypeAlias = dict[int, int]
EDGE_LIST: TypeAlias = list[list[int]]
EDGE_DICT: TypeAlias = dict[int, NDArray[np.int64]]


def build_degrees(n: int, gamma: float, delta: int, zeta: float) -> DEGREE_LIST:
    max_degree = np.floor(n**zeta)
    avail = np.arange(delta, max_degree + 1)

    probabilities = powerlaw_distribution(avail, gamma)

    degrees = np.sort(np.random.choice(avail, size=n, p=probabilities))[::-1]

    if degrees.sum() % 2 == 1:
        degrees[0] += 1

    return degrees


def build_community_sizes(n: int, beta: float, s: int, tau: float) -> NDArray[np.int64]:
    max_community_size = int(np.floor(n**tau))
    max_community_number = int(np.ceil(n / s))
    avail = np.arange(s, max_community_size + 1)

    probabilities = powerlaw_distribution(avail, beta)

    big_list: NDArray[np.int64] = np.random.choice(avail, size=max_community_number, p=probabilities)
    community_sizes: NDArray[np.int64] = np.zeros(max_community_number, dtype=np.int64)

    index = 0
    while community_sizes.sum() < n:
        community_sizes[index] = big_list[index]
        index += 1

    community_sizes = community_sizes[:index]
    excess = community_sizes.sum() - n
    if excess > 0:
        if (community_sizes[-1] - excess) >= s:
            community_sizes[-1] -= excess
        else:
            removed = community_sizes[-1]
            community_sizes = community_sizes[:-1]
            for i in range(removed - excess):
                community_sizes[i % len(community_sizes)] += 1
    return np.sort(community_sizes)[::-1]


def build_communities(community_sizes: NDArray[np.int64]) -> COMMUNITIES:
    communities = {}
    v_last = -1
    for i, c in enumerate(community_sizes):
        communities[i] = [v for v in range(v_last + 1, v_last + 1 + c)]
        v_last += c
    return communities


def assign_degrees(
    degrees: DEGREE_LIST,
    communities: COMMUNITIES,
    community_sizes: NDArray[np.int64],
    xi: float,
) -> DEGREE_SEQUENCE:
    phi = 1 - np.sum(community_sizes**2) / (len(degrees) ** 2)
    deg = {}
    avail = 0
    already_chosen = set()

    lock = 0
    d_previous = degrees[0] + 1

    for i, d in enumerate(degrees):
        if (d < d_previous) and (lock < len(community_sizes)):
            threshold = d * (1 - xi * phi) + 1
            while community_sizes[lock] >= threshold:
                avail = communities[lock][-1]
                lock += 1
                if lock == len(community_sizes):
                    break

        v = np.random.choice(avail)
        while v in already_chosen:
            v = np.random.choice(avail)

        already_chosen.add(v)
        deg[v] = d

        if avail == len(degrees) - 1:
            still_not_chosen_set = set(range(len(degrees))) - already_chosen
            still_not_chosen: NDArray[np.int64] = np.array([v for v in still_not_chosen_set])
            degrees_remaining: NDArray[np.int64] = degrees[i + 1 :]  # noqa: E203

            np.random.shuffle(still_not_chosen)

            deg.update({label: degree for label, degree in zip(still_not_chosen, degrees_remaining)})
            return deg

        d_previous = d
    return deg


# TODO: naming degree list vs degree sequence (as dict)
def split_degrees(
    degrees: dict[int, int],
    communities: COMMUNITIES,
    xi: float,
) -> tuple[dict[int, int], dict[int, int]]:
    deg_c = {v: rand_round((1 - xi) * degrees[v]) for v in degrees}
    for community in communities.values():
        if sum(deg_c[v] for v in community) % 2 == 0:
            continue

        v_max = _get_v_max(deg_c, community)
        deg_c[v_max] += 1
        if deg_c[v_max] > degrees[v_max]:
            deg_c[v_max] -= 2

    deg_b = {v: (degrees[v] - deg_c[v]) for v in degrees}
    return deg_c, deg_b


def _get_v_max(deg_c: dict[int, int], community: list[int]) -> int:
    deg_c_subset = {v: deg_c[v] for v in community}
    max_value = max(deg_c_subset.values())
    for elem, value in deg_c_subset.items():
        if value == max_value:
            return elem
    return community[0]


def configuration_model(degree_sequence: DEGREE_SEQUENCE) -> NDArray[np.int64]:
    labels = list(degree_sequence.keys())
    counts = list(degree_sequence.values())

    # Create an array containing repeated vertices based on their degrees
    vertices = np.repeat(labels, counts)

    # Shuffle the array of vertices
    np.random.shuffle(vertices)

    # Create pairs of vertices to represent edges
    edges = np.array(vertices).reshape(-1, 2)

    return edges


def build_recycle_list(edges: EDGE_DICT) -> list[int]:
    edge_count = {}
    recycle_list = []
    for i, e in edges.items():
        e_left = min(e[0], e[1])
        e_right = max(e[0], e[1])
        try:
            edge_count[e_left][e_right] += 1
            recycle_list.append(i)
        except:
            edge_count[e_left] = {e_right: 1}
            if e_left == e_right:
                recycle_list.append(i)
    return recycle_list


def rewire_edge(
    edges: EDGE_DICT, 
    edge_index: int, 
    skip_set: set, 
    rewire_candidates: list[int], 
    recycle_list: list[int]
) -> tuple[EDGE_DICT, set, list[int]]:
    if edge_index not in skip_set:
        rewire_candidates.remove(edge_index)
        paired_edge_index = np.random.choice(rewire_candidates)
        rewire_candidates.remove(paired_edge_index)
        if paired_edge_index in recycle_list:
            skip_set.add(paired_edge_index)
        edges[edge_index] = np.array([edges[edge_index][0], edges[paired_edge_index][0]])
        edges[paired_edge_index] = np.array([edges[edge_index][1], edges[paired_edge_index][1]])
    return edges, skip_set, rewire_candidates


def push_to_background(
    edges: EDGE_DICT, 
    background_degree_sequence: DEGREE_SEQUENCE, 
    recycle_list: list[int]
) -> tuple[EDGE_DICT, DEGREE_SEQUENCE]:
    for i in recycle_list:
        e = edges.pop(i)
        background_degree_sequence[e[0]] += 1
        background_degree_sequence[e[1]] += 1
    return edges, background_degree_sequence


def rewire(
    edge_list: NDArray[np.int64],
    background_degree_sequence: DEGREE_SEQUENCE, 
    is_community: bool = True
) -> tuple[EDGE_DICT, DEGREE_SEQUENCE]:
    edges = {
        i: edge_list[i] for i in range(len(edge_list))
    }
    recycle_list = build_recycle_list(edges)
    while len(recycle_list) > 0:
        rewire_candidates = list(edges.keys())
        skip_set = set()
        for i in recycle_list:
            edges, skip_set, rewire_candidates = rewire_edge(edges, i, skip_set, rewire_candidates, recycle_list)
        new_recycle_list = build_recycle_list(edges)
        if len(new_recycle_list) >= len(recycle_list) and is_community:
            return push_to_background(edges, background_degree_sequence, new_recycle_list)
        else:
            recycle_list = new_recycle_list
    return edges, background_degree_sequence
        

def build_community_edges(
    community_degree_sequence: DEGREE_SEQUENCE, 
    background_degree_sequence: DEGREE_SEQUENCE, 
    communities: COMMUNITIES
) -> tuple[EDGE_DICT, DEGREE_SEQUENCE]:
    edge_list = []
    for community in communities.values():
        community_edges = configuration_model({v: community_degree_sequence[v] for v in community})
        community_edges, background_degree_sequence = rewire(community_edges, background_degree_sequence)
        edge_list.extend(list(community_edges.values()))
    return edge_list, background_degree_sequence


def add_background_edges(
    edge_list: EDGE_LIST, 
    background_degree_sequence: DEGREE_SEQUENCE
) -> EDGE_DICT:
    background_edges = configuration_model(background_degree_sequence)
    edge_list.extend(background_edges)
    edges = dict(enumerate(edge_list))
    edges, background_degree_sequence = rewire(edges, background_degree_sequence, is_community=False)
    return edges
