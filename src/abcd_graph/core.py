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
    "ABCDGraph",
]

import abc
import random
from dataclasses import dataclass
from typing import (
    Any,
    Optional,
    Tuple,
)

import networkx  # type: ignore[import]
import numpy as np
from numpy.typing import NDArray

from abcd_graph.models import (
    Model,
    configuration_model,
)
from abcd_graph.utils import (
    powerlaw_distribution,
    rand_round,
)


def build_degrees(n: int, gamma: float, delta: int, zeta: float) -> NDArray[np.int64]:
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


def build_communities(community_sizes: NDArray[np.int64]) -> dict[int, list[int]]:
    communities = {}
    v_last = -1
    for i, c in enumerate(community_sizes):
        communities[i] = [v for v in range(v_last + 1, v_last + 1 + c)]
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


def _get_v_max(deg_c: dict[int, int], community: list[int]) -> int:
    deg_c_subset = {v: deg_c[v] for v in community}
    max_value = max(deg_c_subset.values())
    for elem, value in deg_c_subset.items():
        if value == max_value:
            return elem
    return community[0]


@dataclass
class Edge:
    __slots__ = ["v1", "v2"]

    v1: int
    v2: int

    def __post_init__(self) -> None:
        self.to_ordered()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return self.v1 == other.v1 and self.v2 == other.v2

    def __hash__(self) -> int:
        return hash((self.v1, self.v2))

    def to_ordered(self) -> None:
        if self.v1 < self.v2:
            self.v1, self.v2 = self.v2, self.v1

    @property
    def is_loop(self) -> bool:
        return self.v1 == self.v2


class AbstractCommunity(abc.ABC):
    def __init__(self, edges: list[Edge]) -> None:
        self._adj_matrix: dict[Edge, int] = {}
        self._bad_edges: list[Edge] = []

        for edge in edges:
            if edge.is_loop:
                self._bad_edges.append(edge)

            if edge in self._adj_matrix:
                self._bad_edges.append(edge)
                self._adj_matrix[edge] += 1
            else:
                self._adj_matrix[edge] = 1


class Community(AbstractCommunity):
    def push_to_background(self, edges: list[Edge], deg_b: dict[int, int]) -> None:
        for edge in edges:
            if edge.is_loop:
                for i in range(self._adj_matrix[edge]):
                    self._adj_matrix[edge] -= 1
                    if self._adj_matrix[edge] == 0:
                        del self._adj_matrix[edge]

                    deg_b[edge.v1] += 1
                    deg_b[edge.v2] += 1
            else:
                for i in range(self._adj_matrix[edge] - 1):
                    self._adj_matrix[edge] -= 1

                    deg_b[edge.v1] += 1
                    deg_b[edge.v2] += 1

    def rewire_community(self, deg_b: dict[int, int]) -> None:
        while len(self._bad_edges) > 0:
            for edge in self._bad_edges:
                other_edge = choose_other_edge(self._adj_matrix, edge)
                rewire_edge(self._adj_matrix, edge, other_edge)

            new_bad_edges = build_recycle_list(self._adj_matrix)
            if len(new_bad_edges) >= len(self._bad_edges):
                self.push_to_background(new_bad_edges, deg_b)
                return
            else:
                self._bad_edges = new_bad_edges


class BackgroundGraph(AbstractCommunity):
    def __init__(self, edges: list[Edge]) -> None:
        super().__init__(edges)


class MalformedGraphException(Exception):
    pass


class ABCDGraph:
    def __init__(self, deg_b: dict[int, int], deg_c: dict[int, int], model: Optional[Model] = None) -> None:
        self.deg_b = deg_b
        self.deg_c = deg_c
        self.model = model if model else configuration_model

        self.communities: list[Community] = []
        self.background_graph: Optional[BackgroundGraph] = None

        self._adj_matrix: dict[Edge, int] = {}

    @property
    def adj_matrix(self) -> NDArray[np.bool_]:
        if not self.is_proper_abcd:
            raise MalformedGraphException("Graph is not proper ABCD so the adjacency matrix is not accurate")

        adj_matrix = np.zeros((len(self.deg_b), len(self.deg_b)), dtype=bool)
        for edge in self._adj_matrix:
            adj_matrix[edge.v1, edge.v2] = True
            adj_matrix[edge.v2, edge.v1] = True

        return adj_matrix

    @property
    def edges(self) -> list[Tuple[int, int]]:
        return [(edge.v1, edge.v2) for edge in self._adj_matrix]

    @property
    def is_proper_abcd(self) -> bool:
        return len(build_recycle_list(self._adj_matrix)) == 0

    def build_communities(self, communities: dict[int, list[int]]) -> "ABCDGraph":
        for community in communities.values():
            community_edges = self.model({v: self.deg_c[v] for v in community})
            community_obj = Community([Edge(e[0], e[1]) for e in community_edges])
            community_obj.rewire_community(self.deg_b)

            assert len(build_recycle_list(community_obj._adj_matrix)) == 0

            self.communities.append(community_obj)

        return self

    def build_background_edges(self) -> "ABCDGraph":
        edges = [Edge(edge[0], edge[1]) for edge in self.model(self.deg_b)]
        self.background_graph = BackgroundGraph(edges)
        self._adj_matrix = self.background_graph._adj_matrix

        return self

    def combine_edges(self) -> "ABCDGraph":
        for community in self.communities:
            for edge, count in community._adj_matrix.items():
                if edge in self._adj_matrix:
                    self._adj_matrix[edge] += count
                else:
                    self._adj_matrix[edge] = count

        return self

    def rewire_graph(self) -> "ABCDGraph":
        bad_edges = build_recycle_list(self._adj_matrix)

        while len(bad_edges) > 0:
            for edge in bad_edges:
                other_edge = choose_other_edge(self._adj_matrix, edge)
                rewire_edge(self._adj_matrix, edge, other_edge)

            bad_edges = build_recycle_list(self._adj_matrix)

        return self

    def to_igraph(self) -> Any: ...

    def to_networkx(self) -> Any:
        return networkx.Graph(self.edges)

    def draw_communities(self) -> None: ...


def build_recycle_list(adj_matrix: dict[Edge, int]) -> list[Edge]:
    return [edge for edge in adj_matrix.keys() if adj_matrix[edge] > 1 or edge.is_loop]


def choose_other_edge(adj_matrix: dict[Edge, int], edge: Edge) -> Edge:
    edges = list(adj_matrix.keys())
    other_edge = random.choice(edges)
    while other_edge == edge:
        other_edge = random.choice(edges)

    return other_edge


def rewire_edge(adj_matrix: dict[Edge, int], edge: Edge, other_edge: Edge) -> None:
    if edge not in adj_matrix:
        return
    adj_matrix[edge] -= 1

    if adj_matrix[edge] == 0:
        del adj_matrix[edge]

    adj_matrix[other_edge] -= 1
    if adj_matrix[other_edge] == 0:
        del adj_matrix[other_edge]

    new_edge = Edge(edge.v1, other_edge.v1)

    if new_edge in adj_matrix:
        adj_matrix[new_edge] += 1
    else:
        adj_matrix[new_edge] = 1

    new_edge = Edge(edge.v2, other_edge.v2)

    if new_edge in adj_matrix:
        adj_matrix[new_edge] += 1
    else:
        adj_matrix[new_edge] = 1
