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

from typing import Optional

from abcd_graph.callbacks.abstract import (
    ABCDCallback,
    BuildContext,
)
from abcd_graph.exporter import GraphExporter
from abcd_graph.graph.core.abcd_objects import (
    Community,
    GraphImpl,
)
from abcd_graph.graph.core.utils import get_community_color_map
from abcd_graph.models import Model
from abcd_graph.utils import require


class Visualizer(ABCDCallback):
    def __init__(self) -> None:
        self._communities: list[Community] = []
        self._model_used: Optional[Model] = None
        self._exporter: Optional[GraphExporter] = None
        self._graph: Optional[GraphImpl] = None

    def after_build(self, graph: GraphImpl, context: BuildContext, exporter: GraphExporter) -> None:
        self._communities = graph.communities
        self._model_used = context.model_used
        self._exporter = exporter

        self._graph = graph

    @require("matplotlib")
    def draw_community_cdf(self) -> None:
        import matplotlib.pyplot as plt  # type: ignore[import]

        assert self._graph is not None

        actual_cdf = self._graph.actual_community_cdf
        expected_cdf = self._graph.expected_community_cdf

        x_actual = list(actual_cdf.keys())
        x_expected = list(expected_cdf.keys())
        y_actual = list(actual_cdf.values())
        y_expected = list(expected_cdf.values())

        plt.plot(x_actual, y_actual, label="Actual")
        plt.plot(x_expected, y_expected, label="Expected")

        plt.xlabel("Community Size")
        plt.ylabel("CDF")
        plt.legend()
        plt.title("Community size CDF")
        plt.show()

    @require("matplotlib")
    def draw_degree_cdf(self) -> None:
        import matplotlib.pyplot as plt

        assert self._graph is not None

        actual_cdf = self._graph.actual_degree_cdf
        expected_cdf = self._graph.expected_degree_cdf

        x_actual = list(actual_cdf.keys())
        x_expected = list(expected_cdf.keys())
        y_actual = list(actual_cdf.values())
        y_expected = list(expected_cdf.values())

        plt.plot(x_actual, y_actual, label="Actual")
        plt.plot(x_expected, y_expected, label="Expected")

        plt.xlabel("Degree")
        plt.ylabel("CDF")
        plt.legend()
        plt.title("Degree CDF")
        plt.show()

    @require("networkx")
    @require("matplotlib")
    def draw_communities(self) -> None:
        assert self._graph is not None
        if len(self._graph.deg_b) > 100:
            raise ValueError("Drawing communities is only supported for graphs with at most 100 vertices")

        if self._model_used is not None and self._model_used.__name__ != "configuration_model":
            raise NotImplementedError("Drawing communities is only supported for the configuration model")

        import networkx as nx  # type: ignore[import]
        from matplotlib import pyplot as plt

        assert self._exporter is not None

        nx_g = self._exporter.to_networkx()

        color_map = get_community_color_map(communities=self._communities)

        nx.draw(nx_g, node_color=color_map, with_labels=True, font_weight="bold")
        plt.show()
