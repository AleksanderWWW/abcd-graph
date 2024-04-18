# Copyright (c) 2024 Jordan Barrett
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
from abcd_graph.core import (
    assign_degrees,
    build_background_edges,
    build_communities,
    build_community_edges,
    build_community_sizes,
    build_degrees,
    split_degrees,
)


@pytest.mark.parametrize("n", [100, 1000, 10000])
@pytest.mark.parametrize("gamma", [2.1, 2.5, 2.9])
@pytest.mark.parametrize("beta", [1.1, 1.5, 1.9])
def test_core(n, gamma, beta):
    params = ABCDParams(gamma=gamma, beta=beta, delta=5)

    degrees = build_degrees(
        n,
        params.gamma,
        params.delta,
        params.zeta,
    )

    assert len(degrees) == n

    community_sizes = build_community_sizes(
        n,
        params.beta,
        params.s,
        params.tau,
    )

    assert sum(community_sizes) == n

    communities = build_communities(community_sizes)

    deg = assign_degrees(degrees, communities, community_sizes, params.xi)

    assert sum(deg.values()) == degrees.sum()

    deg_c, deg_b = split_degrees(deg, communities, params.xi)

    assert sum(deg_c.values()) + sum(deg_b.values()) == sum(deg.values())

    community_edges = build_community_edges(deg_c, communities)

    background_edges = build_background_edges(deg_b)

    assert 2 * len(community_edges) == sum(deg_c.values())
    assert 2 * len(background_edges) == sum(deg_b.values())
