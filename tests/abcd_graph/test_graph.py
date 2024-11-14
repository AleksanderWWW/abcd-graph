import pytest

from abcd_graph import ABCDGraph


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


def test_xi_matrix(): ...


# TODO: Tests for different param values
# TODO: Tests for outliers
