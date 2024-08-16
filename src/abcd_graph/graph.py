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
from typing import Optional

from abcd_graph.api.abcd_models import (
    Model,
    configuration_model,
)
from abcd_graph.api.abcd_params import ABCDParams
from abcd_graph.callbacks.abstract import (
    ABCDCallback,
    BuildContext,
)
from abcd_graph.core.abcd_objects.abcd_graph import ABCDGraph
from abcd_graph.core.build import (
    assign_degrees,
    build_communities,
    build_community_sizes,
    build_degrees,
    split_degrees,
)
from abcd_graph.core.exporter import GraphExporter
from abcd_graph.logger import construct_logger


class Graph:
    def __init__(
        self,
        params: Optional[ABCDParams] = None,
        n: int = 1000,
        logger: bool = False,
        callbacks: Optional[list[ABCDCallback]] = None,
    ) -> None:

        self.params = params or ABCDParams()
        self.n = n
        self.logger = construct_logger(logger)

        self._graph: Optional[ABCDGraph] = None

        self._exporter: Optional[GraphExporter] = None
        self._callbacks = callbacks or []

    def reset(self) -> None:
        self._graph = None

    @property
    def is_built(self) -> bool:
        return self._graph is not None

    @property
    def exporter(self) -> GraphExporter:
        if not self.is_built:
            raise RuntimeError("Exporter is not available if the graph has not been built.")

        if self._exporter is None:
            raise RuntimeError("Exporter is not available.")

        assert self._exporter is not None

        return self._exporter

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

        try:
            build_start = time.perf_counter()
            build_end = self._build_impl(model)
            context.end_time = datetime.now()
        except Exception as e:
            self.logger.error(f"An error occurred while building the graph: {e}")
            self.reset()
            raise e

        context.raw_build_time = build_end - build_start

        assert self._graph is not None
        self._exporter = GraphExporter(self._graph, self.n)

        for callback in self._callbacks:
            callback.after_build(self._graph, context, self._exporter)

        return self

    def _build_impl(self, model: Model) -> float:
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

        return time.perf_counter()
