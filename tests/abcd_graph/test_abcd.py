from abcd_graph import ABCD
from tests.utils import assert_graph_built


def test_abcd_sample(params):
    sampler = ABCD(1000)
    sample = sampler.sample()
    assert_graph_built(sample)
    assert sample is sampler.graph_
