from unittest.mock import patch

import pytest

from abcd_graph import ABCDGraph
from abcd_graph.callbacks import PropertyCollector
from abcd_graph.params import ABCDParams


def test_property_collector(params):
    props = PropertyCollector()
    graph = ABCDGraph(params, callbacks=[props])

    graph.build()

    assert len(props.degree_sequence) == params.vcount

    assert props.xi_matrix.shape == (len(graph.communities), len(graph.communities))

    assert min(props.actual_community_cdf.values()) >= 0 and round(max(props.actual_community_cdf.values()), 10) <= 1

    assert (
        min(props.expected_community_cdf.values()) >= 0 and round(max(props.expected_community_cdf.values()), 10) <= 1
    )

    assert min(props.actual_degree_cdf.values()) >= 0 and round(max(props.actual_degree_cdf.values()), 10) <= 1

    assert min(props.expected_degree_cdf.values()) >= 0 and round(max(props.expected_degree_cdf.values()), 10) <= 1


@patch("abcd_graph.graph.core.abcd_objects.graph_impl.XiMatrixBuilder.build")
def test_property_collector_lazy_eval_xi_matrix(mock_xi_build):
    props = PropertyCollector()
    graph = ABCDGraph(callbacks=[props])

    graph.build()

    mock_xi_build.assert_not_called()  # xi matrix not built until called for

    _ = props.xi_matrix

    mock_xi_build.assert_called_once()

    _ = props.xi_matrix

    mock_xi_build.assert_called_once()  # xi matrix not rebuilt upon every call


@patch("abcd_graph.graph.core.abcd_objects.graph_impl.GraphImpl._calc_actual_degree_cdf")
def test_property_collector_lazy_eval_actual_degree_cdf(mock_actual_cdf):
    props = PropertyCollector()
    graph = ABCDGraph(callbacks=[props])

    graph.build()

    mock_actual_cdf.assert_not_called()

    _ = props.actual_degree_cdf

    mock_actual_cdf.assert_called_once()


@patch("abcd_graph.graph.core.abcd_objects.graph_impl.GraphImpl._calc_expected_degree_cdf")
def test_property_collector_lazy_eval_expected_degree_cdf(mock_expected_cdf):
    props = PropertyCollector()
    graph = ABCDGraph(callbacks=[props])

    graph.build()

    mock_expected_cdf.assert_not_called()

    _ = props.expected_degree_cdf

    mock_expected_cdf.assert_called_once()


@patch("abcd_graph.graph.core.abcd_objects.graph_impl.GraphImpl._calc_actual_community_cdf")
def test_property_collector_lazy_eval_actual_community_cdf(mock_actual_cdf):
    props = PropertyCollector()
    graph = ABCDGraph(callbacks=[props])

    graph.build()

    mock_actual_cdf.assert_not_called()

    _ = props.actual_community_cdf

    mock_actual_cdf.assert_called_once()


@patch("abcd_graph.graph.core.abcd_objects.graph_impl.GraphImpl._calc_expected_community_cdf")
def test_property_collector_lazy_eval_expected_community_cdf(mock_expected_cdf):
    props = PropertyCollector()
    graph = ABCDGraph(callbacks=[props])

    graph.build()

    mock_expected_cdf.assert_not_called()

    _ = props.expected_community_cdf

    mock_expected_cdf.assert_called_once()


def test_property_collector_failing_methods_with_custom_sequences(params_with_custom_sequences: ABCDParams):
    props = PropertyCollector()
    graph = ABCDGraph(params=params_with_custom_sequences, callbacks=[props])
    graph.build()

    with pytest.raises(RuntimeError):
        props.expected_degree_cdf()

    with pytest.raises(RuntimeError):
        props.expected_community_cdf()
