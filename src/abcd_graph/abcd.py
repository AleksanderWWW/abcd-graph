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

__all__ = [
    "generate_abcd",
]

from typing import (
    TYPE_CHECKING,
    Any,
)

from abcd_graph.core import (
    assign_degrees,
    build_background_edges,
    build_communities,
    build_community_edges,
    build_community_sizes,
    build_degrees,
    split_degrees,
)

if TYPE_CHECKING:
    from abcd_graph.abcd_params import ABCDParams


def generate_abcd(*, params: "ABCDParams", n: int = 1000) -> tuple[list[list[Any]], list[list[Any]]]:
    """
    < short description >
    :param params: ABCD input params (ABCDParams)
    :param n: number of vertices (int) - defaults to 1000
    :return:
    """
    degrees = build_degrees(
        n,
        params.gamma,
        params.delta,
        params.zeta,
    )

    community_sizes = build_community_sizes(
        n,
        params.beta,
        params.s,
        params.tau,
    )
    communities = build_communities(community_sizes)
    deg = assign_degrees(degrees, communities, community_sizes, params.xi)
    deg_c, deg_b = split_degrees(deg, communities, params.xi)
    community_edges = build_community_edges(deg_c, communities)
    background_edges = build_background_edges(deg_b)
    return community_edges, background_edges
