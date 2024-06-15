import pytest

from abcd_graph import (
    ABCDParams,
    Graph,
)
from abcd_graph.api.abcd_models import (
    chung_lu,
    configuration_model,
)


@pytest.mark.parametrize("n", [100, 10000])
@pytest.mark.parametrize("gamma", [2.1, 2.9])
@pytest.mark.parametrize("beta", [1.1, 1.9])
@pytest.mark.parametrize(
    "model",
    [
        configuration_model,
        chung_lu,
    ],
)
def test_graph_creation(n, gamma, beta, model):
    params = ABCDParams(gamma=gamma, beta=beta)
    g = Graph(params, n=n)

    _test_not_built(g)

    g.build(model)
    assert g.is_built
    assert g.is_proper_abcd
    assert g.adj_matrix.shape == (n, n)

    g.reset()

    _test_not_built(g)


def _test_not_built(g: Graph) -> None:
    assert g._model_used is None
    assert not g.is_built
    with pytest.raises(RuntimeError):
        _ = g.is_proper_abcd

    with pytest.raises(RuntimeError):
        _ = g.adj_matrix

    with pytest.raises(RuntimeError):
        _ = g.summary
