from abcd_graph import ABCDGraph


def test_xi_matrix(params):
    g = ABCDGraph(params, logger=False).build()

    xi_matrix = g._graph.xi_matrix

    assert xi_matrix.min() >= 0

    assert xi_matrix.shape == (len(g.communities), len(g.communities))
