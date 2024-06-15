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
from abcd_graph.logger import construct_logger
from abcd_graph.utils import require

if TYPE_CHECKING:
    from igraph import Graph as IGraph  # type: ignore[import]
    from networkx import Graph as NetworkXGraph  # type: ignore[import]

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
    def summary(self) -> dict[str, Any]:
        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

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
    def num_communities(self) -> int:
        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None
        return self._graph.num_communities

    @property
    def num_edges(self) -> int:
        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None
        return len(self._graph.edges)

    @property
    def is_built(self) -> bool:
        return self._graph is not None

    @property
    def is_proper_abcd(self) -> bool:
        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None
        return self._graph.is_proper_abcd

    @property
    def adj_matrix(self) -> NDArray[np.bool_]:
        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        if not self.is_proper_abcd:
            raise MalformedGraphException("Graph is not proper ABCD so the adjacency matrix is not accurate")

        assert self._graph is not None
        return self._graph.to_adj_matrix()

    @require("igraph")
    def to_igraph(self) -> "IGraph":  # type: ignore[no-any-unimported]
        import igraph

        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None
        return igraph.Graph(self._graph.edges)

    @require("networkx")
    def to_networkx(self) -> "NetworkXGraph":  # type: ignore[no-any-unimported]
        import networkx as nx

        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None

        graph = nx.Graph()

        graph.add_nodes_from(range(self.n))
        graph.add_edges_from(self._graph.edges)
        return graph

    @require("networkx")
    @require("matplotlib")
    def draw_communities(self) -> None:
        if self._model_used is not None and self._model_used.__name__ != "configuration_model":
            raise NotImplementedError("Drawing communities is only supported for the configuration model")

        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None

        if not self.is_proper_abcd:
            raise MalformedGraphException("Graph is not proper ABCD so the adjacency matrix is not accurate")

        import matplotlib.colors as colors  # type: ignore[import]
        import networkx as nx
        from matplotlib import pyplot as plt

        colors_list = list(colors.BASE_COLORS.values())[: self.num_communities]

        color_map = []

        nx_g = self.to_networkx()

        for i, community in enumerate(self._graph.communities):
            color = colors_list[i]
            color_map.extend([color] * len(community.vertices))

        nx.draw(nx_g, node_color=color_map, with_labels=True, font_weight="bold")
        plt.show()

    def build(self, model: Optional[Model] = None) -> "Graph":
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
