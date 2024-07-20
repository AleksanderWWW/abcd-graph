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

__all__ = ["ABCDGraph", "Community"]

import abc
import random
from dataclasses import dataclass
from typing import (
    Any,
    Optional,
)

import numpy as np
from numpy.typing import NDArray

from abcd_graph.api.abcd_models import Model
from abcd_graph.typing import (
    Communities,
    DegreeSequence,
)


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


class AbstractGraph(abc.ABC):
    @property
    @abc.abstractmethod
    def adj_dict(self) -> dict[Edge, int]: ...


class AbstractCommunity(AbstractGraph):
    def __init__(self, edges: list[Edge], community_id: int) -> None:
        self.community_id = community_id
        self._adj_dict: dict[Edge, int] = {}
        self._bad_edges: list[Edge] = []

        for edge in edges:
            if edge.is_loop:
                self._bad_edges.append(edge)

            if edge in self.adj_dict:
                self._bad_edges.append(edge)
                self._adj_dict[edge] += 1
            else:
                self._adj_dict[edge] = 1

        self._edges = edges

    @property
    def edges(self) -> list[Edge]:
        return self._edges

    @property
    def adj_dict(self) -> dict[Edge, int]:
        return self._adj_dict


class Community(AbstractCommunity):
    def __init__(self, edges: list[Edge], vertices: list[int], deg_c: DegreeSequence, community_id: int) -> None:
        super().__init__(edges, community_id)

        self.vertices = vertices
        self._deg_c = deg_c

    @property
    def local_deg_c(self) -> DegreeSequence:
        return {k: v for k, v in self._deg_c.items() if k in self.vertices}

    def empirical_xi(self, deg_b: DegreeSequence) -> float:
        return sum(deg_b[i] for i in self.vertices) / (
            sum(deg_b[i] for i in self.vertices) + sum(self.local_deg_c.values())
        )

    def push_to_background(self, edges: list[Edge], deg_b: DegreeSequence) -> None:
        for edge in edges:
            if edge.is_loop:
                for i in range(self.adj_dict[edge]):
                    self.adj_dict[edge] -= 1
                    if self.adj_dict[edge] == 0:
                        del self.adj_dict[edge]

                    self._update_degree_sequences(edge, deg_b)
            else:
                for i in range(self.adj_dict[edge] - 1):
                    self.adj_dict[edge] -= 1

                    self._update_degree_sequences(edge, deg_b)

    def _update_degree_sequences(self, edge: Edge, deg_b: DegreeSequence) -> None:
        deg_b[edge.v1] += 1
        deg_b[edge.v2] += 1
        self._deg_c[edge.v1] -= 1
        self._deg_c[edge.v2] -= 1

    def rewire_community(self, deg_b: DegreeSequence) -> None:
        while len(self._bad_edges) > 0:
            for edge in self._bad_edges:
                other_edge = choose_other_edge(self.adj_dict, edge)
                rewire_edge(self.adj_dict, edge, other_edge)

            new_bad_edges = build_recycle_list(self.adj_dict)
            if len(new_bad_edges) >= len(self._bad_edges):
                self.push_to_background(new_bad_edges, deg_b)
                return
            else:
                self._bad_edges = new_bad_edges


class BackgroundGraph(AbstractCommunity):
    def __init__(self, edges: list[Edge]) -> None:
        super().__init__(edges, community_id=-1)


class ABCDGraph(AbstractGraph):
    def __init__(self, deg_b: dict[int, int], deg_c: dict[int, int]) -> None:
        self.deg_b = deg_b
        self.deg_c = deg_c

        self.communities: list[Community] = []
        self.background_graph: Optional[BackgroundGraph] = None

        self._adj_dict: dict[Edge, int] = {}

    @property
    def degree_sequence(self) -> dict[int, int]:
        deg = {v: 0 for v in range(len(self.deg_b))}
        for e in self.edges:
            deg[e[0]] += 1
            deg[e[1]] += 1
        return deg

    @property
    def adj_dict(self) -> dict[Edge, int]:
        return self._adj_dict

    def to_adj_matrix(self) -> NDArray[np.bool_]:
        adj_matrix = np.zeros((len(self.deg_b), len(self.deg_b)), dtype=bool)
        for edge in self._adj_dict:
            adj_matrix[edge.v1, edge.v2] = True
            adj_matrix[edge.v2, edge.v1] = True

        return adj_matrix

    @property
    def edges(self) -> list[tuple[int, int]]:
        return [(edge.v1, edge.v2) for edge in self._adj_dict]

    @property
    def is_proper_abcd(self) -> bool:
        return len(build_recycle_list(self._adj_dict)) == 0

    @property
    def num_communities(self) -> int:
        return len(self.communities)

    def build_communities(self, communities: Communities, model: Model) -> "ABCDGraph":
        for community_id, community_vertices in communities.items():
            community_edges = model({v: self.deg_c[v] for v in community_vertices})
            community_obj = Community(
                edges=[Edge(e[0], e[1]) for e in community_edges],
                vertices=community_vertices,
                deg_c=self.deg_c,
                community_id=community_id,
            )
            community_obj.rewire_community(self.deg_b)

            assert len(build_recycle_list(community_obj.adj_dict)) == 0

            self.communities.append(community_obj)

        return self

    def build_background_edges(self, model: Model) -> "ABCDGraph":
        edges = [Edge(edge[0], edge[1]) for edge in model(self.deg_b)]
        self.background_graph = BackgroundGraph(edges)
        self._adj_dict = self.background_graph.adj_dict

        return self

    def combine_edges(self) -> "ABCDGraph":
        for community in self.communities:
            for edge, count in community.adj_dict.items():
                if edge in self._adj_dict:
                    self._adj_dict[edge] += count
                else:
                    self._adj_dict[edge] = count

        return self

    def rewire_graph(self) -> "ABCDGraph":
        bad_edges = build_recycle_list(self._adj_dict)

        while len(bad_edges) > 0:
            for edge in bad_edges:
                other_edge = choose_other_edge(self._adj_dict, edge)
                rewire_edge(self._adj_dict, edge, other_edge)

            bad_edges = build_recycle_list(self._adj_dict)

        return self


def build_recycle_list(adj_matrix: dict["Edge", int]) -> list["Edge"]:
    return [edge for edge in adj_matrix.keys() if adj_matrix[edge] > 1 or edge.is_loop]


def choose_other_edge(adj_matrix: dict["Edge", int], edge: "Edge") -> "Edge":
    edges = list(adj_matrix.keys())
    other_edge = random.choice(edges)
    while other_edge == edge:
        other_edge = random.choice(edges)

    return other_edge


def rewire_edge(adj_matrix: dict["Edge", int], edge: "Edge", other_edge: "Edge") -> None:
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
