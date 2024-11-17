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

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from abcd_graph.graph.core.abcd_objects import GraphImpl
from abcd_graph.graph.core.exceptions import MalformedGraphException
from abcd_graph.utils import require

if TYPE_CHECKING:  # pragma: no cover
    from igraph import Graph as IGraph  # type: ignore[import]
    from networkx import Graph as NetworkXGraph  # type: ignore[import]
    from scipy.sparse import csr_matrix  # type: ignore[import]


class GraphExporter:
    def __init__(self, graph: GraphImpl) -> None:
        self._graph: GraphImpl = graph

    @property
    def is_proper_abcd(self) -> bool:
        return self._graph.is_proper_abcd

    def to_adjacency_matrix(self) -> NDArray[np.bool_]:
        if not self.is_proper_abcd:
            raise MalformedGraphException("Graph is not proper ABCD so the adjacency matrix cannot be built")

        assert self._graph is not None
        return self._graph.to_adj_matrix()

    @require("scipy")
    def to_sparse_adjacency_matrix(self) -> "csr_matrix":  # type: ignore[no-any-unimported]
        from scipy.sparse import csr_matrix

        if not self.is_proper_abcd:
            raise MalformedGraphException("Graph is not proper ABCD so the adjacency matrix cannot be built")

        assert self._graph is not None
        return csr_matrix(self.to_adjacency_matrix())

    @require("igraph")
    def to_igraph(self) -> "IGraph":  # type: ignore[no-any-unimported]
        import igraph

        graph = igraph.Graph(self._graph.edges)

        graph.vs["ground_truth_community"] = self._graph.membership_list

        return graph

    @require("networkx")
    def to_networkx(self) -> "NetworkXGraph":  # type: ignore[no-any-unimported]
        import networkx as nx

        graph = nx.Graph()

        graph.add_nodes_from(range(self._graph._params.vcount))
        graph.add_edges_from(self._graph.edges)

        m_list = self._graph.membership_list

        for node in graph.nodes:
            graph.nodes[node]["ground_truth_community"] = m_list[node]

        return graph
