import abc

from abcd_graph.graph.core.abcd_objects.edge import Edge


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
