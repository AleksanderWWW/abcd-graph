import math

import pytest

from abcd_graph.core.utils import rand_round


@pytest.mark.parametrize("value", [0.1, -0.5, 1.9, 0, -100.4])
def test_rand_round(value):
    # when
    rounded = rand_round(value)

    # then
    assert math.floor(value) <= rounded <= math.ceil(value)

    assert isinstance(rounded, int)
