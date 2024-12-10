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

__all__ = ["rand_round", "powerlaw_distribution", "get_community_color_map"]

import math
import random
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:  # pragma: no cover
    from abcd_graph.graph.core.abcd_objects import Community


def rand_round(x: float) -> int:
    p = x - math.floor(x)
    return int(math.floor(x) + 1) if random.uniform(0, 1) <= p else int(math.floor(x))


def powerlaw_distribution(choices: NDArray[np.float64], intensity: float) -> NDArray[np.float64]:
    dist: NDArray[np.float64] = (choices ** (-intensity)) / np.sum(choices ** (-intensity))
    return dist


def get_community_color_map(communities: list["Community"]) -> list[str]:
    import matplotlib.colors as colors  # type: ignore[import]

    colors_list = list(colors.BASE_COLORS.values())[: len(communities)]

    color_map = []

    for i, community in enumerate(communities):
        color = colors_list[i]
        color_map.extend([color] * len(community.vertices))

    return color_map
