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

__all__ = ["ABCDGraph"]

import time
import warnings
from datetime import datetime
from typing import (
    Optional,
    cast,
)

import numpy as np

from abcd_graph.callbacks.abstract import (
    ABCDCallback,
    BuildContext,
)
from abcd_graph.exporter import GraphExporter
from abcd_graph.graph.community import ABCDCommunity
from abcd_graph.graph.core.abcd_objects import GraphImpl
from abcd_graph.graph.core.build import (
    add_outliers,
    assign_degrees,
    build_communities,
    build_community_sizes,
    build_degrees,
    split_degrees,
)
from abcd_graph.logger import construct_logger
from abcd_graph.models import (
    Model,
    configuration_model,
)
from abcd_graph.params import ABCDParams


class ABCDGraph:
    def __init__(
        self,
        params: Optional[ABCDParams] = None,
        logger: bool = False,
        callbacks: Optional[list[ABCDCallback]] = None,
    ) -> None:

        self.params: ABCDParams = params or ABCDParams()

        self._vcount = self.params.vcount

        self.num_outliers = self.params.num_outliers

        self._has_outliers: bool = self.num_outliers > 0

        self._num_regular_vertices = self._vcount - self.num_outliers

        self.logger = construct_logger(logger)

        self._graph: Optional[GraphImpl] = None

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

    @property
    def vcount(self) -> int:
        return self._vcount if self.is_built else 0

    @property
    def edges(self) -> list[tuple[int, int]]:
        return self._graph.edges if self._graph else []

    @property
    def membership_list(self) -> list[int]:
        return self._graph.membership_list if self._graph else []

    @property
    def communities(self) -> list[ABCDCommunity]:
        return (
            [
                ABCDCommunity(
                    community_id=community.community_id,
                    vertices=community.vertices,
                    average_degree=community.average_degree,
                    degree_sequence=community.degree_sequence,
                    empirical_xi=community.empirical_xi,
                )
                for community in self._graph.communities
            ]
            if self._graph
            else []
        )

    def build(self, model: Optional[Model] = None) -> "ABCDGraph":
        if self.is_built:
            warnings.warn("Graph has already been built. Run `reset` and try again.")
            return self

        model = model if model else configuration_model

        context = BuildContext(
            model_used=model,
            start_time=datetime.now(),
            params=self.params,
            number_of_nodes=self._vcount,
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
        self._exporter = GraphExporter(self._graph)

        for callback in self._callbacks:
            callback.after_build(self._graph, context, self._exporter)

        return self

    def _build_impl(self, model: Model) -> float:
        degrees = (
            build_degrees(
                self._num_regular_vertices,
                cast(float, self.params.gamma),
                cast(int, self.params.min_degree),
                cast(int, self.params.max_degree),
            )
            if self.params.degree_sequence is None
            else np.array(self.params.degree_sequence)
        )

        self.logger.info("Building community sizes")

        community_sizes = (
            build_community_sizes(
                self._num_regular_vertices,
                cast(float, self.params.beta),
                cast(int, self.params.min_community_size),
                cast(int, self.params.max_community_size),
            )
            if self.params.community_size_sequence is None
            else np.array(self.params.community_size_sequence)
        )

        self.logger.info("Building communities")

        communities = build_communities(community_sizes)

        self.logger.info("Assigning degrees")

        deg = assign_degrees(degrees, communities, community_sizes, self.params.xi)

        self.logger.info("Splitting degrees")

        deg_c, deg_b = split_degrees(deg, communities, self.params.xi)

        if self._has_outliers:
            self.logger.info("Adding outliers")
            communities, deg_b, deg_c = add_outliers(
                vcount=self._vcount,
                num_outliers=self.num_outliers,
                gamma=cast(float, self.params.gamma),
                min_degree=cast(int, self.params.min_degree),
                max_degree=cast(int, self.params.max_degree),
                communities=communities,
                deg_b=deg_b,
                deg_c=deg_c,
            )

        self._graph = GraphImpl(deg_b, deg_c, params=self.params)

        self.logger.info("Building community edges")
        self._graph.build_communities(communities, model)

        self.logger.info("Building background edges")
        self._graph.build_background_edges(model)

        self.logger.info("Resolving collisions")
        self._graph.combine_edges()

        self._graph.rewire_graph()

        return time.perf_counter()
