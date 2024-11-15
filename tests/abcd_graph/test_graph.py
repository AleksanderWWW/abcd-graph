import pytest

from abcd_graph import ABCDGraph
from abcd_graph.graph.core.constants import OUTLIER_COMMUNITY_ID


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


def assert_graph_built(graph: ABCDGraph):
    assert graph.is_built

    assert graph.exporter is not None
    assert graph.communities != []
    assert graph.edges != []
    assert graph.membership_list != []
    assert graph.vcount == graph.params.vcount


def assert_graph_not_built(graph: ABCDGraph):
    assert not graph.is_built

    with pytest.raises(RuntimeError):
        _ = graph.exporter

    assert graph.communities == []
    assert graph.edges == []
    assert graph.membership_list == []
    assert graph.vcount == 0


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
