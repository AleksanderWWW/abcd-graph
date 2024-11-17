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


@pytest.mark.integration
def test_export_to_igraph(graph):
    i_graph = graph.build().exporter.to_igraph()

    assert i_graph.vcount() == graph.vcount
    assert i_graph.vs["ground_truth_community"] == graph.membership_list
    assert i_graph.ecount() == len(graph.edges)


@pytest.mark.integration
def test_export_to_networkx(graph):
    nx_graph = graph.build().exporter.to_networkx()

    assert nx_graph.number_of_nodes() == graph.vcount
    assert nx_graph.number_of_edges() == len(graph.edges)
    # TODO: Check if the ground truth communities are exported correctly
