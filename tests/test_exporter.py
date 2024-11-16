from unittest.mock import patch

import numpy
import pytest
import scipy.sparse

from abcd_graph.graph.core.exceptions import MalformedGraphException


def test_export_to_adjacency_matrix(graph):
    graph.build()

    assert graph.exporter.is_proper_abcd

    assert isinstance(graph.exporter.to_adjacency_matrix(), numpy.ndarray)


@patch("abcd_graph.exporter.GraphExporter.is_proper_abcd", False)
def test_export_to_adjacency_matrix_not_proper_abcd(graph):
    graph.build()

    with pytest.raises(MalformedGraphException):
        graph.exporter.to_adjacency_matrix()


@pytest.mark.integration
def test_export_to_sparse_adjacency_matrix(graph):
    graph.build()

    assert graph.exporter.is_proper_abcd

    assert scipy.sparse.isspmatrix_csr(graph.exporter.to_sparse_adjacency_matrix())


@pytest.mark.integration
@patch("abcd_graph.exporter.GraphExporter.is_proper_abcd", False)
def test_export_to_sparse_adjacency_matrix_not_proper_abcd(graph):
    graph.build()
    with pytest.raises(MalformedGraphException):
        graph.exporter.to_sparse_adjacency_matrix()
