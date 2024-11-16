from abcd_graph import ABCDGraph
from abcd_graph.callbacks import PropertyCollector


def test_property_collector(params):
    props = PropertyCollector()
    graph = ABCDGraph(params, callbacks=[props])

    graph.build()

    assert len(props.degree_sequence) == params.vcount

    assert props.xi_matrix.shape == (len(graph.communities), len(graph.communities))
