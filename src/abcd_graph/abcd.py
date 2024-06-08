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
    from abcd_graph.api.abcd_params import ABCDParams


class Graph:
    def __init__(
        self,
        params: "ABCDParams",
        n: int = 1000,
        model: Optional[Model] = None,
        logger: bool = False,
    ) -> None:
        self.params = params
        self.n = n
        self.model = model if model else configuration_model
        self.logger = construct_logger(logger)

        self._graph: Optional[ABCDGraph] = None

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
    def to_igraph(self) -> Any:
        import igraph  # type: ignore[import]

        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None
        return igraph.Graph(self._graph.edges)

    @require("networkx")
    def to_networkx(self) -> Any:
        import networkx  # type: ignore[import]

        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        assert self._graph is not None
        return networkx.Graph(self._graph.edges)

    @require("matplotlib")
    def draw_communities(self) -> None: ...

    def build(self) -> "Graph":
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

        self._graph = ABCDGraph(deg_b, deg_c, model=self.model)

        self.logger.info("Building community edges")
        self._graph.build_communities(communities)

        self.logger.info("Building background edges")
        self._graph.build_background_edges()

        self.logger.info("Resolving collisions")
        self._graph.combine_edges()

        self._graph.rewire_graph()

        return self
