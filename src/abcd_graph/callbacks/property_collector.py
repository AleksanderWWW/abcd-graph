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

import numpy as np
from numpy.typing import NDArray

from abcd_graph.callbacks.abstract import (
    ABCDCallback,
    BuildContext,
)
from abcd_graph.core.abcd_objects.abcd_graph import ABCDGraph
from abcd_graph.core.abcd_objects.community import Community
from abcd_graph.core.exporter import GraphExporter


class PropertyCollector(ABCDCallback):
    def __init__(self) -> None:
        self._communities: list[Community] = []

        self._degree_sequence: dict[int, int] = {}

        self._xi_matrix: Optional[NDArray[np.float64]] = None

        self._expected_degree_cdf: dict[int, float] = {}

        self._actual_degree_cdf: dict[int, float] = {}

        self._expected_community_cdf: dict[int, float] = {}

        self._actual_community_cdf: dict[int, float] = {}

    def after_build(self, graph: ABCDGraph, context: BuildContext, exporter: GraphExporter) -> None:
        self._communities = graph.communities

        self._degree_sequence = graph.degree_sequence

        self._xi_matrix = graph.xi_matrix

        self._expected_degree_cdf = graph.expected_degree_cdf

        self._actual_degree_cdf = graph.actual_degree_cdf

        self._expected_community_cdf = graph.expected_community_cdf

        self._actual_community_cdf = graph.actual_community_cdf

    @property
    def vertex_partition(self) -> dict[int, list[int]]:
        return {i: community.vertices for i, community in enumerate(self._communities)}

    @property
    def degree_sequence(self) -> dict[int, int]:
        return self._degree_sequence

    @property
    def xi_matrix(self) -> NDArray[np.float64]:
        assert self._xi_matrix is not None

        return self._xi_matrix

    @property
    def expected_degree_cdf(self) -> dict[int, float]:
        return self._expected_degree_cdf

    @property
    def actual_degree_cdf(self) -> dict[int, float]:
        return self._actual_degree_cdf

    @property
    def expected_community_cdf(self) -> dict[int, float]:
        return self._expected_community_cdf

    @property
    def actual_community_cdf(self) -> dict[int, float]:
        return self._actual_community_cdf
