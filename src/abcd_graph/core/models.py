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
    @abc.abstractmethod
    @property
    def adj_dict(self) -> dict[Edge, int]: ...


class AbstractCommunity(AbstractGraph):
    def __init__(self, edges: list[Edge]) -> None:
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

    @property
    def adj_dict(self) -> dict[Edge, int]:
        return self._adj_dict


class Community(AbstractCommunity):
    def push_to_background(self, edges: list[Edge], deg_b: dict[int, int]) -> None:
        for edge in edges:
            if edge.is_loop:
                for i in range(self.adj_dict[edge]):
                    self.adj_dict[edge] -= 1
                    if self.adj_dict[edge] == 0:
                        del self.adj_dict[edge]

                    deg_b[edge.v1] += 1
                    deg_b[edge.v2] += 1
            else:
                for i in range(self.adj_dict[edge] - 1):
                    self.adj_dict[edge] -= 1

                    deg_b[edge.v1] += 1
                    deg_b[edge.v2] += 1

    def rewire_community(self, deg_b: dict[int, int]) -> None:
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
        super().__init__(edges)


class ABCDGraph(AbstractGraph):
    def __init__(self, deg_b: dict[int, int], deg_c: dict[int, int], model: Model) -> None:
        self.deg_b = deg_b
        self.deg_c = deg_c
        self.model = model

        self.communities: list[Community] = []
        self.background_graph: Optional[BackgroundGraph] = None

        self._adj_dict: dict[Edge, int] = {}

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

    def build_communities(self, communities: dict[int, list[int]]) -> "ABCDGraph":
        for community in communities.values():
            community_edges = self.model({v: self.deg_c[v] for v in community})
            community_obj = Community([Edge(e[0], e[1]) for e in community_edges])
            community_obj.rewire_community(self.deg_b)

            assert len(build_recycle_list(community_obj.adj_dict)) == 0

            self.communities.append(community_obj)

        return self

    def build_background_edges(self) -> "ABCDGraph":
        edges = [Edge(edge[0], edge[1]) for edge in self.model(self.deg_b)]
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
