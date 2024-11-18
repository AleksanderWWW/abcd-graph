from unittest.mock import patch

import pytest

from abcd_graph import ABCDGraph
from abcd_graph.graph.core.constants import OUTLIER_COMMUNITY_ID
from abcd_graph.models import configuration_model
from tests.utils import (
    assert_graph_built,
    assert_graph_not_built,
)


def test_abcd_graph_not_built(params):
    # when
    g = ABCDGraph(params, logger=False)

    # then
    assert_graph_not_built(g)


def test_abcd_graph_built(params):
    # given
    g = ABCDGraph(params, logger=False)

    # when
    g.build()

    # then
    assert_graph_built(g)


def test_abcd_reset_after_build(params):
    # given
    g = ABCDGraph(params, logger=False)

    # when
    g.build()

    # then
    assert_graph_built(g)

    # when
    g.reset()

    # then
    assert_graph_not_built(g)


def test_graph_exporter_raises_exception_if_exporter_is_none(params):
    graph = ABCDGraph(params=params, logger=False).build()
    graph._exporter = None

    with pytest.raises(RuntimeError):
        _ = graph.exporter


@patch("abcd_graph.graph.ABCDGraph._build_impl", side_effect=Exception)
@patch("abcd_graph.graph.ABCDGraph.reset")
def test_graph_build_error_triggers_reset(mock_reset, mock_build_impl):
    graph = ABCDGraph(logger=False)

    with pytest.raises(Exception):
        graph.build()

    mock_build_impl.assert_called_once_with(configuration_model)

    mock_reset.assert_called_once()


# TODO: Tests for different param values


def test_outliers(params_with_outliers):
    g = ABCDGraph(params_with_outliers, logger=False).build()

    assert g.num_outliers == 100

    assert OUTLIER_COMMUNITY_ID in [c.community_id for c in g.communities]

    outlier_community = next(c for c in g.communities if c.community_id == OUTLIER_COMMUNITY_ID)
    assert len(outlier_community.vertices) == 100


def test_outliers_deg_c_is_zero_for_every_outlier(params_with_outliers):
    g = ABCDGraph(params_with_outliers, logger=False).build()

    outlier_community = next(c for c in g.communities if c.community_id == OUTLIER_COMMUNITY_ID)

    deg_c = g._graph.deg_c

    assert all(deg_c[v] == 0 for v in outlier_community.vertices)
