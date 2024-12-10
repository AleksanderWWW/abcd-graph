__all__ = ["Community", "BackgroundGraph"]

from abcd_graph.graph.core.abcd_objects.abstract import AbstractCommunity
from abcd_graph.graph.core.abcd_objects.edge import Edge
from abcd_graph.graph.core.abcd_objects.utils import (
    build_recycle_list,
    choose_other_edge,
    rewire_edge,
)
from abcd_graph.graph.core.constants import BACKGROUND_GRAPH_ID


class Community(AbstractCommunity):
    def __init__(
        self,
        edges: list[Edge],
        vertices: list[int],
        deg_b: dict[int, int],
        deg_c: dict[int, int],
        community_id: int,
    ) -> None:
        super().__init__(edges, community_id)

        self._vertices = vertices
        self._deg_b = deg_b
        self._deg_c = deg_c

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AbstractCommunity):
            return False
        return self.community_id == other.community_id

    def __hash__(self) -> int:
        return hash(self.community_id)

    @property
    def vertices(self) -> list[int]:
        return self._vertices

    @property
    def average_degree(self) -> float:
        return sum(self.degree_sequence.values()) / len(self.vertices)

    @property
    def degree_sequence(self) -> dict[int, int]:
        res = {}
        for vert in self.vertices:
            res[vert] = self._deg_c[vert] + self._deg_b[vert]
        return res

    @property
    def empirical_xi(self) -> float:
        return sum(self._deg_b[i] for i in self.vertices) / (
            sum(self._deg_b[i] + self._deg_c[i] for i in self.vertices)
        )

    def push_to_background(self, edges: list[Edge], deg_b: dict[int, int]) -> None:
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

    def _update_degree_sequences(self, edge: Edge, deg_b: dict[int, int]) -> None:
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
        super().__init__(edges, community_id=-BACKGROUND_GRAPH_ID)
