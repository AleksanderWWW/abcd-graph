import pytest

from abcd_graph import ABCDGraph


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
