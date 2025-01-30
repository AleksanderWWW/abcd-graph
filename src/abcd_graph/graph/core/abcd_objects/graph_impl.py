__all__ = ["GraphImpl"]

from typing import (
    Optional,
    cast,
)

import numpy as np
from numpy.typing import NDArray

from abcd_graph.graph.core.abcd_objects import (
    BackgroundGraph,
    Community,
    Edge,
)
from abcd_graph.graph.core.abcd_objects.abstract import AbstractGraph
from abcd_graph.graph.core.abcd_objects.utils import (
    build_recycle_list,
    choose_other_edge,
    rewire_edge,
)
from abcd_graph.graph.core.constants import OUTLIER_COMMUNITY_ID
from abcd_graph.models import Model
from abcd_graph.params import ABCDParams

UNSUPPORTED_OPERATION_CUSTOM_SEQUENCE_MSG = """Cannot compute {operation_name} because relevant parameters are `None`.
                If you passed custom degree sequence to `ABCDParams()` you cannot use this property.
                Otherwise this might be a bug on our side - please contact the maintainers or submit a GitHub issue.
            """


class GraphImpl(AbstractGraph):
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
        if not all([self._params.gamma, self._params.min_degree, self._params.max_degree]):
            raise RuntimeError(
                UNSUPPORTED_OPERATION_CUSTOM_SEQUENCE_MSG.format(operation_name="expected average degree")
            )

        self._params.gamma = cast(float, self._params.gamma)
        self._params.min_degree = cast(int, self._params.min_degree)
        self._params.max_degree = cast(int, self._params.max_degree)

        bottom: float = sum(
            k ** (-self._params.gamma) for k in range(self._params.min_degree, self._params.max_degree + 1)
        )
        top: float = sum(
            k ** (1 - self._params.gamma) for k in range(self._params.min_degree, self._params.max_degree + 1)
        )

        return top / bottom

    @property
    def actual_degree_cdf(self) -> dict[int, float]:
        return self._calc_actual_degree_cdf()

    def _calc_actual_degree_cdf(self) -> dict[int, float]:
        deg = {v: self.deg_b[v] + self.deg_c[v] for v in self.deg_b}
        sorted_deg = sorted(list(deg.values()))
        val = sorted_deg[0]
        cdf = {val: 1 / self._params.vcount}
        for d in sorted_deg[1:]:
            new_val = d
            if new_val == val:
                cdf[new_val] += 1 / self._params.vcount
            else:
                cdf[new_val] = cdf[val] + 1 / self._params.vcount
            val = new_val
        return cdf

    @property
    def expected_degree_cdf(self) -> dict[int, float]:
        if not all([self._params.gamma, self._params.min_degree, self._params.max_degree]):
            raise RuntimeError(UNSUPPORTED_OPERATION_CUSTOM_SEQUENCE_MSG.format(operation_name="expected degree cdf"))

        return self._calc_expected_degree_cdf()

    def _calc_expected_degree_cdf(self) -> dict[int, float]:
        self._params.gamma = cast(float, self._params.gamma)
        self._params.min_degree = cast(int, self._params.min_degree)
        self._params.max_degree = cast(int, self._params.max_degree)

        cdf = {}
        bottom = sum(k ** (-self._params.gamma) for k in range(self._params.min_degree, self._params.max_degree + 1))

        for d in range(self._params.min_degree, self._params.max_degree + 1):
            cdf[d] = sum(k ** (-self._params.gamma) for k in range(self._params.min_degree, d + 1)) / bottom
        return cdf

    @property
    def actual_average_community_size(self) -> float:
        return self._calc_actual_average_community_size()

    def _calc_actual_average_community_size(self) -> float:
        volume = sum(
            len(c.vertices) for c in self.communities if c.community_id != OUTLIER_COMMUNITY_ID
        )  # Excluding outliers
        num_communities = len([c for c in self.communities if c.community_id != OUTLIER_COMMUNITY_ID])
        return volume / num_communities

    @property
    def expected_average_community_size(self) -> float:
        if not all([self._params.beta, self._params.min_community_size, self._params.max_community_size]):
            raise RuntimeError(
                UNSUPPORTED_OPERATION_CUSTOM_SEQUENCE_MSG.format(operation_name="expected average community size")
            )

        return self._calc_expected_average_community_size()

    def _calc_expected_average_community_size(self) -> float:
        self._params.beta = cast(float, self._params.beta)
        self._params.min_community_size = cast(int, self._params.min_community_size)
        self._params.max_community_size = cast(int, self._params.max_community_size)

        bottom: float = sum(
            k ** (-self._params.beta)
            for k in range(self._params.min_community_size, self._params.max_community_size + 1)
        )
        top: float = sum(
            k ** (1 - self._params.beta)
            for k in range(self._params.min_community_size, self._params.max_community_size + 1)
        )
        return top / bottom

    @property
    def actual_community_cdf(self) -> dict[int, float]:
        return self._calc_actual_community_cdf()

    def _calc_actual_community_cdf(self) -> dict[int, float]:
        L = len([c for c in self.communities if c.community_id != OUTLIER_COMMUNITY_ID])  # Excluding outliers
        sizes = {c: len(c.vertices) for c in self.communities if c.community_id != OUTLIER_COMMUNITY_ID}
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
        if not all([self._params.beta, self._params.min_community_size, self._params.max_community_size]):
            raise RuntimeError(
                UNSUPPORTED_OPERATION_CUSTOM_SEQUENCE_MSG.format(operation_name="expected community cdf")
            )

        return self._calc_expected_community_cdf()

    def _calc_expected_community_cdf(self) -> dict[int, float]:
        self._params.beta = cast(float, self._params.beta)
        self._params.min_community_size = cast(int, self._params.min_community_size)
        self._params.max_community_size = cast(int, self._params.max_community_size)

        cdf = {}
        bottom = sum(
            k ** (-self._params.beta)
            for k in range(self._params.min_community_size, self._params.max_community_size + 1)
        )
        for s in range(self._params.min_community_size, self._params.max_community_size + 1):
            cdf[s] = sum(k ** (-self._params.beta) for k in range(self._params.min_community_size, s + 1)) / bottom
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
        return len(self.communities) if self._params.num_outliers == 0 else len(self.communities) - 1

    @property
    def membership_list(self) -> list[int]:
        result = []

        for community in self.communities:
            result += [community.community_id] * len(community.vertices)

        return result

    def build_communities(self, communities: dict[int, list[int]], model: Model) -> "GraphImpl":
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

    def build_background_edges(self, model: Model) -> "GraphImpl":
        edges = [Edge(edge[0], edge[1]) for edge in model(self.deg_b)]
        self.background_graph = BackgroundGraph(edges)
        self._adj_dict = self.background_graph.adj_dict

        return self

    def combine_edges(self) -> "GraphImpl":
        for community in self.communities:
            for edge, count in community.adj_dict.items():
                if edge in self._adj_dict:
                    self._adj_dict[edge] += count
                else:
                    self._adj_dict[edge] = count

        return self

    def rewire_graph(self) -> "GraphImpl":
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
        for c in self.communities:
            for v in c.vertices:
                self.location[v] = c.community_id

    def _build_actual_matrix(self) -> None:
        for edge in self.adj_matrix:
            self.actual_betweenness_matrix[self.location[edge.v1]][self.location[edge.v2]] += 1
            self.actual_betweenness_matrix[self.location[edge.v2]][self.location[edge.v1]] += 1

    def _build_expectation_matrix(self) -> None:
        # Pre-compute community volumes and empirical xi's before looping
        vol = {c.community_id: sum(c.degree_sequence.values()) for c in self.communities}
        empirical_xi = {c.community_id: c.empirical_xi for c in self.communities}
        bottom = sum(self.deg_b.values()) - 1
        for c_i in self.communities:
            for c_j in self.communities:
                if c_i.community_id == OUTLIER_COMMUNITY_ID:
                    vol_i = float(vol[OUTLIER_COMMUNITY_ID])
                else:
                    vol_i = vol[c_i.community_id] * empirical_xi[c_i.community_id]
                if c_j.community_id == OUTLIER_COMMUNITY_ID:
                    vol_j = float(vol[OUTLIER_COMMUNITY_ID])
                else:
                    vol_j = vol[c_j.community_id] * empirical_xi[c_j.community_id]
                top = vol_i * vol_j

                self.expected_betweenness_matrix[c_i.community_id][c_j.community_id] = top / bottom
                self.expected_betweenness_matrix[c_j.community_id][c_i.community_id] = top / bottom

    def _build_normalized_matrix(self) -> None:
        for c_i in self.communities:
            for c_j in self.communities:
                if c_i == c_j and c_i.community_id != OUTLIER_COMMUNITY_ID:
                    self.normalized_betweeness_matrix[c_i.community_id][c_j.community_id] = (1 - c_i.empirical_xi) / (
                        1 - self.xi
                    )
                else:
                    self.normalized_betweeness_matrix[c_i.community_id][c_j.community_id] = (
                        self.actual_betweenness_matrix[c_i.community_id][c_j.community_id]
                        / self.expected_betweenness_matrix[c_i.community_id][c_j.community_id]
                    )

    def build(self) -> NDArray[np.float64]:
        self._build_location()
        self._build_actual_matrix()
        self._build_expectation_matrix()
        self._build_normalized_matrix()

        return self.normalized_betweeness_matrix
