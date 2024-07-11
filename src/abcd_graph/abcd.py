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
    "Graph",
]

import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

import numpy as np
from numpy.typing import NDArray

from abcd_graph.api.abcd_models import (
    Model,
    configuration_model,
)
from abcd_graph.core.build import (
    assign_degrees,
    build_communities,
    build_community_sizes,
    build_degrees,
    split_degrees,
)
from abcd_graph.core.exceptions import MalformedGraphException
from abcd_graph.core.models import ABCDGraph
from abcd_graph.core.utils import get_community_color_map
from abcd_graph.logger import construct_logger
from abcd_graph.utils import (
    require,
    require_graph_built,
)

if TYPE_CHECKING:
    from igraph import Graph as IGraph  # type: ignore[import]
    from networkx import Graph as NetworkXGraph  # type: ignore[import]
    from scipy.sparse import csr_matrix  # type: ignore[import]

    from abcd_graph.api.abcd_params import ABCDParams


class Graph:
    def __init__(
        self,
        params: "ABCDParams",
        n: int = 1000,
        logger: bool = False,
    ) -> None:
        self.params = params
        self.n = n
        self.logger = construct_logger(logger)

        self._graph: Optional[ABCDGraph] = None

        self._model_used: Optional[Model] = None

    def reset(self) -> None:
        self._graph = None
        self._model_used = None

    @property
    @require_graph_built
    def summary(self) -> dict[str, Any]:
        assert self._graph is not None
        assert self._model_used is not None
        return {
            "number_of_nodes": self.n,
            "number_of_edges": self.num_edges,
            "number_of_communities": self.num_communities,
            "model": self._model_used.__name__,
            "is_proper_abcd": self.is_proper_abcd,
        }

    @property
    @require_graph_built
    def num_communities(self) -> int:
        assert self._graph is not None
        return self._graph.num_communities

    @property
    @require_graph_built
    def num_edges(self) -> int:
        assert self._graph is not None
        return len(self._graph.edges)

    @property
    def is_built(self) -> bool:
        return self._graph is not None

    @property
    @require_graph_built
    def is_proper_abcd(self) -> bool:
        assert self._graph is not None
        return self._graph.is_proper_abcd

    @require_graph_built
    def to_adjacency_matrix(self) -> NDArray[np.bool_]:
        if not self.is_proper_abcd:
            raise MalformedGraphException("Graph is not proper ABCD so the adjacency matrix cannot be built")

        assert self._graph is not None
        return self._graph.to_adj_matrix()

    @require("scipy")
    @require_graph_built
    def to_sparse_adjacency_matrix(self) -> "csr_matrix":  # type: ignore[no-any-unimported]
        from scipy.sparse import csr_matrix

        if not self.is_proper_abcd:
            raise MalformedGraphException("Graph is not proper ABCD so the adjacency matrix cannot be built")

        assert self._graph is not None
        return csr_matrix(self.to_adjacency_matrix())

    @require("igraph")
    @require_graph_built
    def to_igraph(self) -> "IGraph":  # type: ignore[no-any-unimported]
        import igraph

        assert self._graph is not None
        return igraph.Graph(self._graph.edges)

    @require("networkx")
    @require_graph_built
    def to_networkx(self) -> "NetworkXGraph":  # type: ignore[no-any-unimported]
        import networkx as nx

        assert self._graph is not None

        graph = nx.Graph()

        graph.add_nodes_from(range(self.n))
        graph.add_edges_from(self._graph.edges)
        return graph

    @require("networkx")
    @require("matplotlib")
    @require_graph_built
    def draw_communities(self) -> None:
        if self._model_used is not None and self._model_used.__name__ != "configuration_model":
            raise NotImplementedError("Drawing communities is only supported for the configuration model")

        assert self._graph is not None

        if not self.is_proper_abcd:
            warnings.warn("Graph is not proper ABCD so the community coloring may not be accurate")

        import networkx as nx
        from matplotlib import pyplot as plt  # type: ignore[import]

        nx_g = self.to_networkx()

        color_map = get_community_color_map(communities=self._graph.communities)

        nx.draw(nx_g, node_color=color_map, with_labels=True, font_weight="bold")
        plt.show()

    def build(self, model: Optional[Model] = None) -> "Graph":
        if self.is_built:
            warnings.warn("Graph has already been built. Run `reset` and try again.")
            return self

        model = model if model else configuration_model

        self._model_used = model

        degrees = build_degrees(
            self.n,
            self.params.gamma,
            self.params.delta,
            self.params.zeta,
        )

        self.logger.info("Building community sizes")

        community_sizes = build_community_sizes(
            self.n,
            self.params.beta,
            self.params.s,
            self.params.tau,
        )

        self.logger.info("Building communities")

        communities = build_communities(community_sizes)

        self.logger.info("Assigning degrees")

        deg = assign_degrees(degrees, communities, community_sizes, self.params.xi)

        self.logger.info("Splitting degrees")

        deg_c, deg_b = split_degrees(deg, communities, self.params.xi)

        self._graph = ABCDGraph(deg_b, deg_c)

        self.logger.info("Building community edges")
        self._graph.build_communities(communities, model)

        self.logger.info("Building background edges")
        self._graph.build_background_edges(model)

        self.logger.info("Resolving collisions")
        self._graph.combine_edges()

        self._graph.rewire_graph()

        return self

    @property
    @require_graph_built
    def vertex_partition(self) -> dict[int, list[int]]:
        assert self._graph is not None

        return {i: community.vertices for i, community in enumerate(self._graph.communities)}

    @require_graph_built
    def to_edge_list(self) -> NDArray[np.int64]:
        assert self._graph is not None

        return np.array(self._graph.edges).reshape(-1, 2)

    #The empirical xi is the fraction of background edges to total edges
    @property
    @require_graph_built
    def empirical_xi(self) -> float:
        assert self._graph is not None

        num_edges = len(self._graph.edges)
        num_community_edges = sum(len(community.edges) for community in self._graph.communities)
        return 1-(num_community_edges/num_edges)

    #This should be the same as self._graph.deg_b + self._graph.deg_c
    @property
    @require_graph_built
    def degree_sequence(self) -> dict[int, int]:
        assert self._graph is not None

        deg = {v: 0 for v in range(self.n)}
        for e in self._graph.edges:
            deg[e[0]] += 1
            deg[e[1]] += 1
        return deg
