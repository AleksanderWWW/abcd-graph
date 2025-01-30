# Copyright (c) 2024 Jordan Barrett & Aleksander Wojnarowicz
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
    "build_communities",
    "build_degrees",
    "assign_degrees",
    "split_degrees",
    "build_community_sizes",
    "add_outliers",
]

from typing import Any

import numpy as np
from numpy.typing import NDArray

from abcd_graph.graph.core.constants import OUTLIER_COMMUNITY_ID
from abcd_graph.graph.core.utils import (
    powerlaw_distribution,
    rand_round,
)


def build_degrees(n: int, gamma: float, min_degree: int, max_degree: int) -> NDArray[np.int64]:
    avail = np.arange(min_degree, max_degree + 1, dtype=float)

    probabilities = powerlaw_distribution(avail, gamma)

    degrees = np.sort(np.random.choice(avail, size=n, p=probabilities))[::-1]

    if degrees.sum() % 2 == 1:
        degrees[0] += 1

    return degrees


def build_community_sizes(n: int, beta: float, min_community_size: int, max_community_size: int) -> NDArray[np.int64]:
    max_community_number = int(np.ceil(n / min_community_size))
    avail = np.arange(min_community_size, max_community_size + 1, dtype=float)

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
        if (community_sizes[-1] - excess) >= min_community_size:
            community_sizes[-1] -= excess
        else:
            removed = community_sizes[-1]
            community_sizes = community_sizes[:-1]
            for i in range(removed - excess):
                community_sizes[i % len(community_sizes)] += 1
    return np.sort(community_sizes)[::-1]


def build_communities(community_sizes: NDArray[np.int64]) -> dict[int, list[int]]:
    communities = {}
    v_last = 0
    for i, c in enumerate(community_sizes):
        communities[i] = [v for v in range(v_last, v_last + c)]
        v_last += c
    return communities


def assign_degrees(
    degrees: NDArray[np.int64],
    communities: dict[int, list[int]],
    community_sizes: NDArray[np.int64],
    xi: float,
) -> dict[int, Any]:
    phi = 1 - np.sum(community_sizes**2) / (len(degrees) ** 2)
    deg = {}
    avail = communities[0][-1]
    already_chosen: set[int] = set()

    lock = 0
    d_previous = degrees[0] + 1

    for i, d in enumerate(degrees):
        if lock_needs_update(d, d_previous, lock, len(community_sizes)):
            threshold = calculate_threshold(d, xi, float(phi))
            lock, avail = update_lock(threshold, lock, avail, community_sizes, communities)

        d_previous = d

        v = choose_new_vertex(avail, already_chosen)

        already_chosen.add(v)
        deg[v] = d

        if avail == len(degrees) - 1:
            return assign_remaining_degrees(i, degrees, already_chosen, deg)

    return deg


def choose_new_vertex(avail: int, already_chosen: set[int]) -> int:
    avail_set = set(range(avail)) - already_chosen

    if not avail_set:
        return max(already_chosen) + 1

    return int(np.random.choice(list(avail_set))) if avail_set else avail


def lock_needs_update(degree: int, previous_degree: int, lock: int, num_communities: int) -> bool:
    return (degree < previous_degree) and (lock < num_communities)


def calculate_threshold(d: int, xi: float, phi: float) -> float:
    return d * (1 - xi * phi) + 1


def update_lock(
    threshold: float,
    lock: int,
    avail: int,
    community_sizes: NDArray[np.int64],
    communities: dict[int, list[int]],
) -> tuple[int, int]:
    while community_sizes[lock] >= threshold:
        avail = communities[lock][-1]
        lock += 1
        if lock == len(community_sizes):
            break
    return lock, avail


def assign_remaining_degrees(
    degree_index: int,
    degrees: NDArray[np.int64],
    already_chosen: set[int],
    deg: dict[int, Any],
) -> dict[int, Any]:
    still_not_chosen_set = set(range(len(degrees))) - already_chosen
    still_not_chosen: NDArray[np.int64] = np.array([v for v in still_not_chosen_set])
    degrees_remaining: NDArray[np.int64] = degrees[degree_index + 1 :]  # noqa: E203

    np.random.shuffle(still_not_chosen)

    deg.update({label: degree for label, degree in zip(still_not_chosen, degrees_remaining)})
    return deg


def split_degrees(
    degrees: dict[int, int],
    communities: dict[int, list[int]],
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


def add_outliers(
    *,
    vcount: int,
    num_outliers: int,
    gamma: float,
    min_degree: int,
    max_degree: int,
    communities: dict[int, list[int]],
    deg_b: dict[int, int],
    deg_c: dict[int, int],
) -> tuple[dict[int, list[int]], dict[int, int], dict[int, int]]:
    regular_vertices = vcount - num_outliers
    outlier_degrees = build_degrees(num_outliers, gamma, min_degree, max_degree)
    communities = communities | {OUTLIER_COMMUNITY_ID: list(range(regular_vertices, vcount))}
    deg_b = deg_b | {regular_vertices + i: outlier_degrees[i] for i in range(num_outliers)}
    deg_c = deg_c | {regular_vertices + i: 0 for i in range(num_outliers)}

    return communities, deg_b, deg_c


def _get_v_max(deg_c: dict[int, int], community: list[int]) -> int:
    deg_c_subset = {v: deg_c[v] for v in community}
    return max(deg_c_subset, key=deg_c_subset.__getitem__)
