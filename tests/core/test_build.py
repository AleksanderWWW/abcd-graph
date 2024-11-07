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
import random

import numpy as np
import pytest

from abcd_graph.core.build import (
    build_communities,
    build_community_sizes,
    build_degrees,
    update_lock,
)


@pytest.mark.parametrize("n", [100, 500, 1000, 5000, 10000])
def test_build_degrees(n):
    gamma = random.uniform(2, 3)
    min_degree = random.randint(1, 10)
    max_degree = random.randint(10, 50)

    result = build_degrees(n, gamma, min_degree, max_degree)

    assert len(result) == n
    assert result.sum() % 2 == 0

    assert result.min() >= min_degree
    assert result.max() <= max_degree + 1


@pytest.mark.parametrize("n", [100, 500, 1000, 5000, 10000])
def test_build_community_sizes(n):
    beta = random.uniform(1, 2)
    min_community_size = random.randint(10, 20)
    max_community_size = random.randint(50, 80)

    result = build_community_sizes(n, beta, min_community_size, max_community_size)

    assert result.sum() == n

    assert result.min() >= min_community_size
    assert result.max() <= max_community_size


def test_build_communities():
    community_sizes = np.array([random.randint(10, 80) for _ in range(10)])

    communities = build_communities(community_sizes)

    for idx, value in enumerate(community_sizes):
        assert len(communities[idx]) == value


class TestAssignDegrees:
    def test_update_lock(self):
        community_sizes = np.array([10, 20, 30, 40])[::-1]

        lock = 2

        threshold = 15

        communities = {0: list(range(40)), 1: list(range(40, 70)), 2: list(range(70, 90)), 3: list(range(90, 100))}

        avail = communities[lock - 1][-1]

        lock_after, avail_after = update_lock(threshold, lock, avail, community_sizes, communities)

        assert lock_after == 3
        assert avail_after == 90 - 1
