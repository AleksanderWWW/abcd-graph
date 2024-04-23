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
from abcd_graph.logger import (
    LoggerType,
    construct_logger,
)

if TYPE_CHECKING:
    from abcd_graph.abcd_params import ABCDParams


def generate_abcd(
    *,
    params: "ABCDParams",
    n: int = 1000,
    logger: LoggerType = False,
) -> tuple[list[list[Any]], list[list[Any]]]:
    """
    < short description >
    :param params: ABCD input params (ABCDParams)
    :param n: number of vertices (int) - defaults to 1000
    :param logger: logger object (ABCDLogger | bool) - defaults to False
    :return:
    """
    abcd_logger = construct_logger(logger)

    abcd_logger.info("Generating ABCD graph")

    abcd_logger.info("Building degrees")
    degrees = build_degrees(
        n,
        params.gamma,
        params.delta,
        params.zeta,
    )

    abcd_logger.info("Building community sizes")

    community_sizes = build_community_sizes(
        n,
        params.beta,
        params.s,
        params.tau,
    )

    abcd_logger.info("Building communities")

    communities = build_communities(community_sizes)

    abcd_logger.info("Assigning degrees")

    deg = assign_degrees(degrees, communities, community_sizes, params.xi)

    abcd_logger.info("Splitting degrees")

    deg_c, deg_b = split_degrees(deg, communities, params.xi)

    abcd_logger.info("Building community edges")

    community_edges = build_community_edges(deg_c, communities)

    abcd_logger.info("Building background edges")

    background_edges = build_background_edges(deg_b)

    abcd_logger.info("ABCD graph generated")

    return community_edges, background_edges
