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
from abcd_graph.exporter import GraphExporter
from abcd_graph.graph.core.abcd_objects import (
    Community,
    GraphImpl,
)


class PropertyCollector(ABCDCallback):
    def __init__(self) -> None:
        self._graph: Optional[GraphImpl] = None

        self._communities: list[Community] = []

        self._degree_sequence: dict[int, int] = {}

        self._xi_matrix: Optional[NDArray[np.float64]] = None

        self._expected_degree_cdf: dict[int, float] = {}

        self._actual_degree_cdf: dict[int, float] = {}

        self._expected_community_cdf: dict[int, float] = {}

        self._actual_community_cdf: dict[int, float] = {}

    def after_build(self, graph: GraphImpl, context: BuildContext, exporter: GraphExporter) -> None:
        self._graph = graph

    @property
    def degree_sequence(self) -> dict[int, int]:
        if not self._degree_sequence:
            self._degree_sequence = self._graph.degree_sequence  # type: ignore[union-attr]

        return self._degree_sequence

    @property
    def xi_matrix(self) -> NDArray[np.float64]:
        if self._xi_matrix is None:
            self._xi_matrix = self._graph.xi_matrix  # type: ignore[union-attr]
        return self._xi_matrix

    @property
    def expected_degree_cdf(self) -> dict[int, float]:
        if not self._expected_degree_cdf:
            self._expected_degree_cdf = self._graph.expected_degree_cdf  # type: ignore[union-attr]

        return self._expected_degree_cdf

    @property
    def actual_degree_cdf(self) -> dict[int, float]:
        if not self._actual_degree_cdf:
            self._actual_degree_cdf = self._graph.actual_degree_cdf  # type: ignore[union-attr]

        return self._actual_degree_cdf

    @property
    def expected_community_cdf(self) -> dict[int, float]:
        if not self._expected_community_cdf:
            self._expected_community_cdf = self._graph.expected_community_cdf  # type: ignore[union-attr]

        return self._expected_community_cdf

    @property
    def actual_community_cdf(self) -> dict[int, float]:
        if not self._actual_community_cdf:
            self._actual_community_cdf = self._graph.actual_community_cdf  # type: ignore[union-attr]

        return self._actual_community_cdf
