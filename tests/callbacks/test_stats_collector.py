import pytest

from abcd_graph import ABCDGraph
from abcd_graph.callbacks import StatsCollector
from abcd_graph.models import (
    chung_lu,
    configuration_model,
)
from abcd_graph.params import ABCDParams


def test_stats_collector(params):
    stats = StatsCollector()
    graph = ABCDGraph(params, callbacks=[stats])

    graph.build()

    assert isinstance(stats.statistics, dict)

    assert stats.fetch_statistic("model_used") == configuration_model.__name__
    assert stats.fetch_statistic("params") == params
    assert stats.fetch_statistic("number_of_nodes") == params.vcount
    assert stats.fetch_statistic("number_of_communities") == len(graph.communities)

    assert "start_time" in stats.statistics
    assert "end_time" in stats.statistics
    assert "time_to_build" in stats.statistics


def test_stats_collector_chung_lu_model(params):
    stats = StatsCollector()
    graph = ABCDGraph(params, callbacks=[stats])
    graph.build(model=chung_lu)

    assert stats.fetch_statistic("model_used") == chung_lu.__name__


def test_stats_collector_failing_methods_with_custom_sequences(params_with_custom_sequences: ABCDParams):
    stats = StatsCollector()
    graph = ABCDGraph(params=params_with_custom_sequences, callbacks=[stats])

    with pytest.raises(RuntimeError):
        graph.build()
