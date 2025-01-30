# Copyright (c) 2024 Jordan Barrett & Aleksander Wojnarowicz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from abcd_graph import ABCDParams
from abcd_graph.params import (
    DEFAULT_BETA_VALUE,
    DEFAULT_GAMMA_VALUE,
)


def test_abcd_params_negative_vcount():
    with pytest.raises(ValueError):
        ABCDParams(vcount=-1)


def test_abcd_params_invalid_gamma():
    with pytest.raises(ValueError):
        ABCDParams(
            gamma=1.5, min_degree=1, max_degree=30, beta=1.5, max_community_size=100, xi=0.5, min_community_size=2
        )


def test_abcd_params_invalid_beta():
    with pytest.raises(ValueError):
        ABCDParams(
            gamma=2.5, min_degree=1, max_degree=30, beta=0.5, max_community_size=100, xi=0.5, min_community_size=2
        )


def test_abcd_params_invalid_tau():
    with pytest.raises(ValueError):
        ABCDParams(
            gamma=2.5, min_degree=1, max_degree=30, beta=1.5, max_community_size=5000, xi=0.5, min_community_size=2
        )


def test_abcd_params_invalid_xi():
    with pytest.raises(ValueError):
        ABCDParams(
            gamma=2.5, min_degree=1, max_degree=30, beta=1.5, max_community_size=100, xi=1.5, min_community_size=2
        )


def test_abcd_params_invalid_min_degree():
    with pytest.raises(ValueError):
        ABCDParams(min_degree=0, max_degree=30)

    with pytest.raises(ValueError):
        ABCDParams(min_degree=30, max_degree=20)


def test_abcd_params_invalid_min_community_size():
    with pytest.raises(ValueError):
        ABCDParams(min_community_size=110, max_community_size=100)


def test_abcd_params_proper_init():
    ABCDParams(gamma=2.5, min_degree=1, max_degree=30, beta=1.5, max_community_size=100, xi=0.5, min_community_size=2)
    assert True


def test_abcd_params_default_init():
    ABCDParams()
    assert True


def test_num_outliers_cannot_be_negative():
    with pytest.raises(ValueError):
        ABCDParams(num_outliers=-1)


def test_num_outliers_cannot_be_greater_than_vcount():
    with pytest.raises(ValueError):
        ABCDParams(vcount=1000, num_outliers=1001)


def test_custom_sequences_defaults():
    ABCDParams(
        degree_sequence=[9] + [1] * 9,
        community_size_sequence=(5, 5),
        vcount=10,
    )


def test_custom_sequences_fail_with_params_provided():
    with pytest.raises(ValueError):
        ABCDParams(
            degree_sequence=[9] + [1] * 9,
            community_size_sequence=(5, 5),
            vcount=10,
            gamma=DEFAULT_GAMMA_VALUE,
            beta=DEFAULT_BETA_VALUE,
        )


def test_custom_sequences_fail_wrong_vcount():
    with pytest.raises(ValueError):
        ABCDParams(
            degree_sequence=[9] + [1] * 9,
            community_size_sequence=(5, 5),
            vcount=100,
        )
