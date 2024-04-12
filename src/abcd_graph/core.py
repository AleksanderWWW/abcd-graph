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
    "configuration_model",
    "build_degrees",
    "build_community_sizes",
    "build_communities",
    "assign_degrees",
    "split_degrees",
    "build_community_edges",
    "build_background_edges",
]

import random

import numpy as np
from numpy.typing import NDArray
from typing_extensions import TypeAlias

from abcd_graph.utils import (
    powerlaw_distribution,
    rand_round,
)

COMMUNITIES: TypeAlias = dict[int, list[int]]
DEGREE_LIST: TypeAlias = list[int]
DEGREE_SEQUENCE: TypeAlias = dict[int, int]


def configuration_model(degree_sequence: dict) -> list[list[int]]:
    l = []  # noqa: E741
    for v in degree_sequence.keys():
        l.extend([v] * degree_sequence[v])
    random.shuffle(l)
    E = [[l[2 * i], l[2 * i + 1]] for i in range(int(np.floor(sum(degree_sequence.values()) / 2)))]
    return E


def build_degrees(n: int, gamma: float, delta: int, zeta: float) -> DEGREE_LIST:
    max_degree = int(np.floor(n**zeta))
    avail = list(range(delta, max_degree + 1))

    probabilities = powerlaw_distribution(avail, gamma)

    degrees = list(reversed(sorted(np.random.choice(avail, size=n, p=probabilities))))
    if sum(degrees) % 2 == 1:
        degrees[0] += 1
    return degrees


def build_community_sizes(n: int, beta: float, s: int, tau: float) -> NDArray[np.int64]:
    max_community_size = np.floor(n**tau)
    max_community_number = np.ceil(n / s)
    avail = range(s, max_community_size + 1)

    probabilities = powerlaw_distribution(avail, beta)

    big_list: NDArray[np.int64] = np.random.choice(avail, size=max_community_number, p=probabilities)
    community_sizes: NDArray[np.int64] = np.array([], dtype=np.int64)
    index = 0
    while community_sizes.sum() < n:
        np.append(community_sizes, big_list[index])
        index += 1
    excess = community_sizes.sum() - n
    if excess > 0:
        if (community_sizes[-1] - excess) >= s:
            community_sizes[-1] -= excess
        else:
            removed = community_sizes[-1]
            community_sizes = community_sizes[:-1]
            for i in range(removed - excess):
                community_sizes[i] += 1
    return np.sort(community_sizes)[::-1]


def build_communities(community_sizes: NDArray[np.int64]) -> COMMUNITIES:
    communities = {}
    v_last = -1
    for i, c in enumerate(community_sizes):
        communities[i] = [v for v in range(v_last + 1, v_last + 1 + c)]
        v_last += c
    return communities


def assign_degrees(
    degrees: list[int],
    communities: COMMUNITIES,
    community_sizes: NDArray[np.int64],
    xi: float,
) -> DEGREE_SEQUENCE:
    phi = 1 - sum(c**2 for c in community_sizes) / (len(degrees) ** 2)
    deg = {}
    avail = []
    lock = 0
    d_previous = degrees[0] + 1
    for d in degrees:
        if (d < d_previous) and (lock < len(community_sizes)):
            threshold = d * (1 - xi * phi) + 1
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
def split_degrees(
    degrees: dict[int, int],
    communities: COMMUNITIES,
    xi: float,
) -> tuple[dict[int, int], dict[int, int]]:
    deg_c = {v: rand_round((1 - xi) * degrees[v]) for v in degrees.keys()}
    for community in communities.values():
        if sum(deg_c[v] for v in community) % 2 == 1:
            v_max = deg_c[community[0]]
            for v in community:
                if deg_c[v] > deg_c[v_max]:
                    v_max = v
            deg_c[v_max] += 1
            if deg_c[v_max] > degrees[v_max]:
                deg_c[v_max] -= 2
    deg_b = {v: (degrees[v] - deg_c[v]) for v in degrees.keys()}
    return deg_c, deg_b


def build_community_edges(community_degrees: dict[int, int], communities: COMMUNITIES) -> list[list]:
    community_edges = []
    for community in communities.values():
        community_edges.extend(configuration_model({v: community_degrees[v] for v in community}))
    return community_edges


def build_background_edges(background_degrees: dict[int, int]) -> list[list]:
    return configuration_model(background_degrees)
