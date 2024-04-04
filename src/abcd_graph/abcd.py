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
    "ABCDParams",
]

from dataclasses import dataclass
from typing import Any

from abcd_graph.core import build_degrees, build_community_sizes, build_communities, assign_degrees, split_degrees, \
    build_community_edges, build_background_edges


#n: number of vertices
#gamma: power-law parameter for degrees, between 2 and 3
#delta: min degree
#zeta: parameter for max degree, between 0 and 1
#beta: power-law parameter for community sizes, between 1 and 2
#s: min community size
#tau: parameter for max community size, between zeta and 1
#xi: noise parameter, between 0 and 1
@dataclass
class ABCDParams:
    # TODO: add docstrings and validation of parameters
    """"""
    gamma: float
    delta: int
    zeta: float
    beta: float
    tau: float
    xi: float
    s: int


# pydantic -> data validation
# defensive programming
def generate_abcd(*, n: int, params: ABCDParams) -> tuple[list[list[Any]], list[list[Any]]]:
    """
    < short description >
    :param n: number of vertices (int)
    :param params: ABCD input params (ABCDParams)
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
