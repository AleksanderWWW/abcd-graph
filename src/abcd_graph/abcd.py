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

import time
import warnings
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Optional,
)

from abcd_graph.api.abcd_models import (
    Model,
    configuration_model,
)
from abcd_graph.callbacks.abstract import (
    ABCDCallback,
    BuildContext,
)
from abcd_graph.core.abcd_objects.graph import ABCDGraph
from abcd_graph.core.build import (
    assign_degrees,
    build_communities,
    build_community_sizes,
    build_degrees,
    split_degrees,
)
from abcd_graph.core.exporter import GraphExporter
from abcd_graph.logger import construct_logger

if TYPE_CHECKING:
    from abcd_graph.api.abcd_params import ABCDParams


class Graph:
    def __init__(
        self, params: "ABCDParams", n: int = 1000, logger: bool = False, callbacks: Optional[list[ABCDCallback]] = None
    ) -> None:
        self.params = params
        self.n = n
        self.logger = construct_logger(logger)

        self._graph: Optional[ABCDGraph] = None

        self._model_used: Optional[Model] = None

        self.exporter: Optional[GraphExporter] = None
        self._callbacks = callbacks or []

    def reset(self) -> None:
        self._graph = None
        self._model_used = None

    @property
    def is_built(self) -> bool:
        return self._graph is not None

    def build(self, model: Optional[Model] = None) -> "Graph":
        if self.is_built:
            warnings.warn("Graph has already been built. Run `reset` and try again.")
            return self

        model = model if model else configuration_model

        context = BuildContext(
            model_used=model,
            start_time=datetime.now(),
            params=self.params,
            number_of_nodes=self.n,
        )

        for callback in self._callbacks:
            callback.before_build(context)

        build_start = time.perf_counter()

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

        self._graph = ABCDGraph(deg_b, deg_c, params=self.params)

        self.logger.info("Building community edges")
        self._graph.build_communities(communities, model)

        self.logger.info("Building background edges")
        self._graph.build_background_edges(model)

        self.logger.info("Resolving collisions")
        self._graph.combine_edges()

        self._graph.rewire_graph()

        build_end = time.perf_counter()

        context.end_time = datetime.now()
        context.raw_build_time = build_end - build_start

        self.exporter = GraphExporter(self._graph, self.n)

        for callback in self._callbacks:
            callback.after_build(self._graph, context, self.exporter)

        return self
