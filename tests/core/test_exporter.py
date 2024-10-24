from unittest.mock import (
    Mock,
    patch,
)

import pytest

from abcd_graph.core.abcd_objects.graph_impl import GraphImpl
from abcd_graph.core.exceptions import MalformedGraphException
from abcd_graph.core.exporter import GraphExporter


@patch("abcd_graph.core.abcd_objects.graph_impl.GraphImpl", return_value=Mock(spec=GraphImpl))
def test_graph_exporter_adj_matrix(mock_graph):
    # given
    exporter = GraphExporter(mock_graph)

    mock_graph.is_proper_abcd = True

    mock_graph.to_adj_matrix.return_value = [[0, 1], [1, 0]]

    # when
    result = exporter.to_adjacency_matrix()

    # then
    assert result == [[0, 1], [1, 0]]
    mock_graph.to_adj_matrix.assert_called_once()


@patch("abcd_graph.core.abcd_objects.graph_impl.GraphImpl", return_value=Mock(spec=GraphImpl))
def test_graph_exporter_improper_graph(mock_graph):
    # given
    exporter = GraphExporter(mock_graph)

    mock_graph.is_proper_abcd = False

    # then
    with pytest.raises(MalformedGraphException):
        exporter.to_adjacency_matrix()

    with pytest.raises(MalformedGraphException):
        exporter.to_sparse_adjacency_matrix()
