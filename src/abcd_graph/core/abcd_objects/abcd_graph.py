from typing import Optional

import numpy as np
from numpy.typing import NDArray

from abcd_graph.api.abcd_models import Model
from abcd_graph.api.abcd_params import ABCDParams
from abcd_graph.core.abcd_objects.abstract import AbstractGraph
from abcd_graph.core.abcd_objects.community import (
    BackgroundGraph,
    Community,
)
from abcd_graph.core.abcd_objects.edge import Edge
from abcd_graph.core.abcd_objects.utils import (
    build_recycle_list,
    choose_other_edge,
    rewire_edge,
)
from abcd_graph.core.typing import Communities


class ABCDGraph(AbstractGraph):
    def __init__(self, deg_b: dict[int, int], deg_c: dict[int, int], params: ABCDParams) -> None:
        self.deg_b = deg_b
        self.deg_c = deg_c

        self._params = params

        self.communities: list[Community] = []
        self.background_graph: Optional[BackgroundGraph] = None

        self._adj_dict: dict[Edge, int] = {}

    @property
    def average_degree(self) -> float:
        return (sum(self.deg_b.values()) + sum(self.deg_c.values())) / len(self.deg_b)

    @property
    def expected_average_degree(self) -> float:
        d_max = int(np.floor(len(self.deg_b) ** self._params.zeta))
        bottom: float = sum(k ** (-self._params.gamma) for k in range(self._params.delta, d_max + 1))
        top: float = sum(k ** (1 - self._params.gamma) for k in range(self._params.delta, d_max + 1))

        return top / bottom

    @property
    def actual_degree_cdf(self) -> dict[int, float]:
        n = len(self.deg_b)
        deg = {v: self.deg_b[v] + self.deg_c[v] for v in self.deg_b}
        sorted_deg = sorted(list(deg.values()))
        val = sorted_deg[0]
        cdf = {val: 1 / n}
        for d in sorted_deg[1:]:
            new_val = d
            if new_val == val:
                cdf[new_val] += 1 / n
            else:
                cdf[new_val] = cdf[val] + 1 / n
            val = new_val
        return cdf

    @property
    def expected_degree_cdf(self) -> dict[int, float]:
        cdf = {}
        n = len(self.deg_b)
        gamma = self._params.gamma
        d_min = self._params.delta
        d_max = int(np.floor(n**self._params.zeta))
        bottom = sum(k ** (-gamma) for k in range(d_min, d_max + 1))
        for d in range(d_min, d_max + 1):
            cdf[d] = sum(k ** (-gamma) for k in range(d_min, d + 1)) / bottom
        return cdf

    @property
    def actual_average_community_size(self) -> float:
        volume = sum(len(c.vertices) for c in self.communities)
        return volume / len(self.communities)

    @property
    def expected_average_community_size(self) -> float:
        n = len(self.deg_b)
        beta = self._params.beta
        c_min = self._params.s
        c_max = int(np.floor(n**self._params.tau))
        bottom: float = sum(k ** (-beta) for k in range(c_min, c_max + 1))
        top: float = sum(k ** (1 - beta) for k in range(c_min, c_max + 1))
        return top / bottom

    @property
    def actual_community_cdf(self) -> dict[int, float]:
        L = len(self.communities)
        sizes = {c: len(c.vertices) for c in self.communities}
        sorted_sizes = sorted(list(sizes.values()))
        val = sorted_sizes[0]
        cdf = {val: 1 / L}
        for s in sorted_sizes[1:]:
            new_val = s
            if new_val == val:
                cdf[new_val] += 1 / L
            else:
                cdf[new_val] = cdf[val] + 1 / L
            val = new_val
        return cdf

    @property
    def expected_community_cdf(self) -> dict[int, float]:
        cdf = {}
        n = len(self.deg_b)
        beta = self._params.beta
        c_min = self._params.s
        c_max = int(np.floor(n**self._params.tau))
        bottom = sum(k ** (-beta) for k in range(c_min, c_max + 1))
        for s in range(c_min, c_max + 1):
            cdf[s] = sum(k ** (-beta) for k in range(c_min, s + 1)) / bottom
        return cdf

    @property
    def num_loops(self) -> int:
        assert self.background_graph is not None

        return (
            sum(community.diagnostics["num_loops"] for community in self.communities)
            + self.background_graph.diagnostics["num_loops"]
        )

    @property
    def num_multi_edges(self) -> int:
        assert self.background_graph is not None

        return (
            sum(community.diagnostics["num_multi_edges"] for community in self.communities)
            + self.background_graph.diagnostics["num_multi_edges"]
        )

    @property
    def xi_matrix(self) -> NDArray[np.float64]:
        if self._params.xi == 0:
            raise ValueError("xi_matrix only available if xi > 0")

        return XiMatrixBuilder(self._params.xi, self.communities, self._adj_dict, self.deg_b).build()

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


class XiMatrixBuilder:
    def __init__(
        self,
        xi: float,
        communities: list[Community],
        adj_matrix: dict[Edge, int],
        deg_b: dict[int, int],
    ) -> None:
        self.xi = xi
        self.communities = communities
        self._community_len = len(communities)
        self.adj_matrix = adj_matrix
        self.deg_b = deg_b

        self.location: dict[int, int] = {}
        self.actual_betweenness_matrix = np.zeros((self._community_len, self._community_len))
        self.expected_betweenness_matrix = np.zeros((self._community_len, self._community_len))
        self.normalized_betweeness_matrix = np.zeros((self._community_len, self._community_len))

    def _build_location(self) -> None:
        for i, c in enumerate(self.communities):
            for v in c.vertices:
                self.location[v] = i

    def _build_actual_matrix(self) -> None:
        for edge in self.adj_matrix:
            self.actual_betweenness_matrix[self.location[edge.v1]][self.location[edge.v2]] += 1
            self.actual_betweenness_matrix[self.location[edge.v2]][self.location[edge.v1]] += 1

    def _build_expectation_matrix(self) -> None:
        bottom = sum(self.deg_b.values()) - 1
        for i, c_i in enumerate(self.communities):
            for j, c_j in enumerate(self.communities):
                vol_i = sum(c_i.degree_sequence.values()) * c_i.empirical_xi
                vol_j = sum(c_j.degree_sequence.values()) * c_j.empirical_xi
                top = vol_i * vol_j
                self.expected_betweenness_matrix[i][j] = top / bottom
                self.expected_betweenness_matrix[j][i] = top / bottom

    def _build_normalized_matrix(self) -> None:
        for i, c_i in enumerate(self.communities):
            for j, c_j in enumerate(self.communities):
                if i == j:
                    self.normalized_betweeness_matrix[i][j] = (1 - c_i.empirical_xi) / (1 - self.xi)
                else:
                    self.normalized_betweeness_matrix[i][j] = (
                        self.actual_betweenness_matrix[i][j] / self.expected_betweenness_matrix[i][j]
                    )

    def build(self) -> NDArray[np.float64]:
        self._build_location()
        self._build_actual_matrix()
        self._build_expectation_matrix()
        self._build_normalized_matrix()

        return self.normalized_betweeness_matrix
