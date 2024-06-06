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

__all__ = ["rand_round", "powerlaw_distribution", "require"]

import math
import random
from functools import wraps
from typing import Callable

import numpy as np
from numpy.typing import NDArray
from typing_extensions import (
    ParamSpec,
    TypeVar,
)

P = ParamSpec("P")
R = TypeVar("R")


def require(package_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def deco(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except ImportError as e:
                raise ImportError(
                    f"Package '{package_name}' is required to use '{func.__name__}'. Run "
                    f"`pip install abcd_graph[{package_name}]` to install it."
                ) from e

        return wrapper

    return deco


def rand_round(x: float) -> int:
    p = x - math.floor(x)
    return int(math.floor(x) + 1) if random.uniform(0, 1) <= p else int(math.floor(x))


def powerlaw_distribution(choices: NDArray[np.int64], intensity: float) -> NDArray[np.float64]:
    dist: NDArray[np.float64] = (choices ** (-intensity)) / np.sum(choices ** (-intensity))
    return dist
