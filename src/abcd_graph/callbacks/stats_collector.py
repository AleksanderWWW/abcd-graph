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

__all__ = ["StatsCollector"]

from typing import Any

from abcd_graph.callbacks.abstract import (
    ABCDCallback,
    BuildContext,
)
from abcd_graph.exporter import GraphExporter
from abcd_graph.graph.core.abcd_objects.graph_impl import GraphImpl


class StatsCollector(ABCDCallback):
    def __init__(self) -> None:
        self._statistics: dict[str, Any] = {}

    @property
    def statistics(self) -> dict[str, Any]:
        return self._statistics

    def log_statistic(self, key: str, value: Any) -> None:
        self._statistics[key] = value

    def fetch_statistic(self, key: str) -> Any:
        return self._statistics[key]

    def before_build(self, context: BuildContext) -> None:
        self.log_statistic("model_used", context.model_used.__name__)
        self.log_statistic("params", context.params)
        self.log_statistic("number_of_nodes", context.number_of_nodes)

    def after_build(self, graph: "GraphImpl", context: BuildContext, exporter: GraphExporter) -> None:
        _ = exporter

        self.log_statistic("start_time", context.start_time)
        self.log_statistic("end_time", context.end_time)
        self.log_statistic("time_to_build", context.raw_build_time)

        self.log_statistic("number_of_edges", len(graph.edges))
        self.log_statistic("number_of_communities", graph.num_communities)
        self.log_statistic("expected_average_degree", graph.expected_average_degree)
        self.log_statistic("actual_average_degree", graph.average_degree)
        self.log_statistic("expected_average_community_size", graph.expected_average_community_size)
        self.log_statistic("actual_average_community_size", graph.actual_average_community_size)
        self.log_statistic("number_of_loops", graph.num_loops)
        self.log_statistic("number_of_multi_edges", graph.num_multi_edges)

        self.log_statistic("empirical_xi", get_empirical_xi(graph))


def get_empirical_xi(graph: GraphImpl) -> float:
    num_community_edges = sum(len(community.edges) for community in graph.communities)
    return 1 - (num_community_edges / len(graph.edges))
