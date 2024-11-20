from unittest.mock import patch

from abcd_graph import ABCDGraph
from abcd_graph.callbacks import PropertyCollector


def test_property_collector(params):
    props = PropertyCollector()
    graph = ABCDGraph(params, callbacks=[props])

    graph.build()

    assert len(props.degree_sequence) == params.vcount

    assert props.xi_matrix.shape == (len(graph.communities), len(graph.communities))


@patch("abcd_graph.graph.core.abcd_objects.graph_impl.XiMatrixBuilder.build")
def test_property_collector_lazy_eval(mock_xi_build):
    props = PropertyCollector()
    graph = ABCDGraph(callbacks=[props])

    graph.build()

    mock_xi_build.assert_not_called()  # xi matrix not built until called for

    _ = props.xi_matrix

    mock_xi_build.assert_called_once()

    _ = props.xi_matrix

    mock_xi_build.assert_called_once()  # xi matrix not rebuilt upon every call
