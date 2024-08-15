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

from abcd_graph import ABCDParams
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

        self._diagnostics = {
            "num_loops": 0,
            "num_multi_edges": 0,
        }

        for edge in edges:
            if edge.is_loop:
                self._bad_edges.append(edge)
                self._diagnostics["num_loops"] += 1

            if edge in self.adj_dict:
                self._bad_edges.append(edge)
                self._adj_dict[edge] += 1
                self._diagnostics["num_multi_edges"] += 1
            else:
                self._adj_dict[edge] = 1

        self._edges = edges

    @property
    def edges(self) -> list[Edge]:
        return self._edges

    @property
    def adj_dict(self) -> dict[Edge, int]:
        return self._adj_dict

    @property
    def diagnostics(self) -> dict[str, int]:
        return self._diagnostics


class Community(AbstractCommunity):
    def __init__(
        self,
        edges: list[Edge],
        vertices: list[int],
        deg_b: DegreeSequence,
        deg_c: DegreeSequence,
        community_id: int,
    ) -> None:
        super().__init__(edges, community_id)

        self._vertices = vertices
        self._deg_b = deg_b
        self._deg_c = deg_c

    @property
    def vertices(self) -> list[int]:
        return self._vertices

    @property
    def average_degree(self) -> float:
        return sum(self.degree_sequence.values()) / len(self.vertices)

    @property
    def degree_sequence(self) -> DegreeSequence:
        res = {}
        for vert in self.vertices:
            res[vert] = self._deg_c[vert] + self._deg_b[vert]
        return res

    @property
    def local_deg_c(self) -> DegreeSequence:
        return {k: v for k, v in self._deg_c.items() if k in self.vertices}

    @property
    def empirical_xi(self) -> float:
        return sum(self._deg_b[i] for i in self.vertices) / (
            sum(self._deg_b[i] for i in self.vertices) + sum(self.local_deg_c.values())
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

    def rewire_community(self) -> None:
        while len(self._bad_edges) > 0:
            for edge in self._bad_edges:
                other_edge = choose_other_edge(self.adj_dict, edge)
                rewire_edge(self.adj_dict, edge, other_edge)

            new_bad_edges = build_recycle_list(self.adj_dict)
            if len(new_bad_edges) >= len(self._bad_edges):
                self.push_to_background(new_bad_edges, self._deg_b)
                return
            else:
                self._bad_edges = new_bad_edges


class BackgroundGraph(AbstractCommunity):
    def __init__(self, edges: list[Edge]) -> None:
        super().__init__(edges, community_id=-1)


class ABCDGraph(AbstractGraph):
    def __init__(self, deg_b: dict[int, int], deg_c: dict[int, int], params: ABCDParams) -> None:
        self.deg_b = deg_b
        self.deg_c = deg_c

        self._params = params

        self.communities: list[Community] = []
        self.background_graph: Optional[BackgroundGraph] = None

        self._adj_dict: dict[Edge, int] = {}

    #Maybe we should change the name to just ``average_degree'', and similarly for ``average_community_size''
    @property
    def actual_average_degree(self) -> float:
        volume = sum(self.deg_b.values()) + sum(self.deg_c.values())
        return volume/len(self.deg_b)

    @property
    def expected_average_degree(self) -> float:
        n = len(self.deg_b)
        gamma = self._params.gamma
        d_min = self._params.delta
        d_max = int(np.floor(n**(self._params.zeta)))
        bottom = sum(k**(-gamma) for k in range(d_min, d_max+1))
        top = sum(k**(1-gamma) for k in range(d_min, d_max+1))
        return top/bottom

    #For ``correctness'', I'm adding the actual and expected cdf as properties
    @property
    def actual_degree_cdf(self) -> dict[int, float]:
        n = len(self.deg_b)
        deg = {v: sum(self.deg_b[v] + self.deg_c[v]) for v in self.deg_b}
        sorted_deg = sorted(list(deg.values()))
        val = sorted_deg[0]
        cdf = {val: 1/n}
        for d in sorted_deg[1:]:
            new_val = d
            if new_val == val:
                cdf[new_val] += 1/n
            else:
                cdf[new_val] = cdf[val] + 1/n
            val = new_val
        return cdf

    @property
    def expected_degree_cdf(self) -> dict[int, float]:
        cdf = {}
        n = len(self.deg_b)
        gamma = self._params.gamma
        d_min = self._params.delta
        d_max = int(np.floor(n**(self._params.zeta)))
        bottom = sum(k**(-gamma) for k in range(d_min, d_max+1))
        for d in range(d_min, d_max+1):
            cdf[d] = sum(k**(-gamma) for k in range(d_min, d+1))/bottom
        return cdf

    @property
    def actual_average_community_size(self) -> float:
        volume = sum(len(c.vertices) for c in self.communities)
        return volume/len(self.communities)

    @property
    def expected_average_community_size(self) -> float:
        n = len(self.deg_b)
        beta = self._params.beta
        c_min = self._params.s
        c_max = int(np.floor(n**(self._params.tau)))
        bottom = sum(k**(-beta) for k in range(c_min, c_max+1))
        top = sum(k**(1-beta) for k in range(c_min, c_max+1))
        return top/bottom

    @property
    def actual_community_cdf(self) -> dict[int, float]:
        L = len(self.communities)
        sizes = {c: len(c.vertices) for c in self.communities}
        sorted_sizes = sorted(list(sizes.values()))
        val = sorted_sizes[0]
        cdf = {val: 1/L}
        for s in sorted_sizes[1:]:
            new_val = s
            if new_val == val:
                cdf[new_val] += 1/L
            else:
                cdf[new_val] = cdf[val] + 1/L
            val = new_val
        return cdf

    @property
    def expected_community_cdf(self) -> dict[int, float]:
        cdf = {}
        n = len(self.deg_b)
        beta = self._params.beta
        c_min = self._params.s
        c_max = int(np.floor(n**(self._params.tau)))
        bottom = sum(k**(-beta) for k in range(c_min, c_max+1))
        for s in range(c_min, c_max+1):
            cdf[s] = sum(k**(-beta) for k in range(c_min, s+1))/bottom
        return cdf

    @property
    def num_loops(self) -> int:
        return sum(community.diagnostics["num_loops"] for community in self.communities) \
            + self.background_graph.diagnostics["num_loops"]

    @property
    def num_multi_edges(self) -> int:
        return sum(community.diagnostics["num_multi_edges"] for community in self.communities) \
            + self.background_graph.diagnostics["num_multi_edges"]

    #Name should be changed to ``normalized_xi_matrix''
    @property
    def xi_matrix(self) -> NDArray[np.float64]:
        xi = self._params.xi
        if xi == 0:
            print("xi_matrix only available if xi > 0")
            return

        #First building a dict pointing vertices to their community 
        location = {}
        for i, c in enumerate(self.communities):
            for v in c.vertices:
                location[v] = i

        #Next, building a matrix counting edges between communities
        L = len(self.communities)
        num_edges_between = np.zeros((L, L))
        for edge in self._adj_dict:
            num_edges_between[location[edge.v1]][location[edge.v2]] += 1
            num_edges_between[location[edge.v2]][location[edge.v1]] += 1

        #Now the expectation matrix
        expected_num = np.zeros((L, L))
        bottom = sum(self.deg_b.values())-1
        for i, c_i in enumerate(self.communities):
            for j, c_j in enumerate(self.communities):
                vol_i = sum(c_i.degree_sequence.values())*c_i.empirical_xi
                vol_j = sum(c_j.degree_sequence.values())*c_j.empirical_xi
                top = vol_i*vol_j
                expected_num[i][j] = top/bottom
                expected_num[j][i] = top/bottom

        #Finally, the normalized matrix
        res = np.zeros((L, L))
        for i, c_i in enumerate(self.communities):
            for j, c_j in enumerate(self.communities):
                if i == j:
                    res[i][j] = (1-c_i.empirical_xi)/(1-xi)
                else:
                    res[i][j] = num_edges_between[i][j]/expected_num[i][j]
        return res

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
                deg_b=self.deg_b,
                deg_c=self.deg_c,
                community_id=community_id,
            )
            community_obj.rewire_community()

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
