from unittest.mock import patch

import pytest

from abcd_graph import (
    ABCDGraph,
    ABCDParams,
)
from abcd_graph.callbacks import Visualizer
from abcd_graph.models import chung_lu


def test_visualizer_raises_exception_if_more_than_100_nodes():
    visualizer = Visualizer()
    graph = ABCDGraph(callbacks=[visualizer])

    graph.build()

    with pytest.raises(ValueError):
        visualizer.draw_communities()


def test_visualizer_not_supporting_models_other_than_configuration_model():
    visualizer = Visualizer()
    graph = ABCDGraph(params=ABCDParams(vcount=60, max_community_size=50), callbacks=[visualizer])

    graph.build(model=chung_lu)

    with pytest.raises(NotImplementedError):
        visualizer.draw_communities()


@patch("matplotlib.pyplot.show")
def test_visualizer(mock_show):
    visualizer = Visualizer()
    graph = ABCDGraph(params=ABCDParams(vcount=60, max_community_size=50), callbacks=[visualizer])

    graph.build()

    visualizer.draw_communities()

    mock_show.assert_called_once()


@patch("matplotlib.pyplot.show")
def test_visualizer_draw_community_cdf(mock_show):
    visualizer = Visualizer()
    graph = ABCDGraph(params=ABCDParams(vcount=60, max_community_size=50), callbacks=[visualizer])

    graph.build()

    visualizer.draw_community_cdf()

    mock_show.assert_called_once()


@patch("matplotlib.pyplot.show")
def test_visualizer_draw_degree_cdf(mock_show):
    visualizer = Visualizer()
    graph = ABCDGraph(params=ABCDParams(vcount=60, max_community_size=50), callbacks=[visualizer])

    graph.build()

    visualizer.draw_degree_cdf()

    mock_show.assert_called_once()
