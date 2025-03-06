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

__all__ = ["ABCDParams"]

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

DEFAULT_GAMMA_VALUE: float = 2.5
DEFAULT_MIN_DEGREE: int = 5
DEFAULT_MAX_DEGREE: int = 30

DEFAULT_BETA_VALUE: float = 1.5
DEFAULT_MIN_COMMUNITY_SIZE: int = 20
DEFAULT_MAX_COMMUNITY_SIZE: int = 250


@dataclass
class ABCDParams:
    vcount: int = 1000
    gamma: float | None = None  # 2.5
    beta: float | None = None  # 1.5
    xi: float = 0.25
    min_degree: int | None = None  # 5
    max_degree: int | None = None  # 30
    min_community_size: int | None = None  # 20
    max_community_size: int | None = None  # 250
    degree_sequence: Sequence[int] | NDArray[np.int64] | None = None
    community_size_sequence: Sequence[int] | NDArray[np.int64] | None = None
    num_outliers: int = 0

    def __post_init__(self) -> None:
        if self.degree_sequence is not None:
            if any([self.gamma is not None, self.min_degree is not None, self.max_degree is not None]):
                raise ValueError("cannot pass both `degree_sequence` and any of (`gamma`, `min_degree`, `max_degree`")
            self.degree_sequence = np.sort(np.array(self.degree_sequence))[::-1]

            if sum(self.degree_sequence) % 2 != 0:
                raise ValueError("The sum of a custom degree sequence must be even")

            if max(self.degree_sequence) >= self.vcount:
                raise ValueError("None of the custom degrees can be larger than the total vcount")
        else:
            self.gamma = self.gamma if self.gamma is not None else DEFAULT_GAMMA_VALUE
            self.min_degree = self.min_degree if self.min_degree is not None else DEFAULT_MIN_DEGREE
            self.max_degree = self.max_degree if self.max_degree is not None else DEFAULT_MAX_DEGREE

            if self.gamma < 2 or self.gamma > 3:
                raise ValueError("gamma must be between 2 and 3")

            if self.min_degree < 1 or self.min_degree > self.max_degree:
                raise ValueError("min_degree must be between 1 and max_degree")

        if self.community_size_sequence is not None:
            if any([self.beta is not None, self.min_community_size is not None, self.max_community_size is not None]):
                raise ValueError(
                    "cannot pass both `community_size_sequence` and any of \
                                 (`beta`, `min_community_size`, `max_community_size`)"
                )
            self.community_size_sequence = np.sort(np.array(self.community_size_sequence))[::-1]

            if sum(self.community_size_sequence) != self.vcount:
                raise ValueError("The sum of custom community sizes must be equal to the total vcount")
        else:
            self.beta = self.beta if self.beta is not None else DEFAULT_BETA_VALUE
            self.min_community_size = (
                self.min_community_size if self.min_community_size is not None else DEFAULT_MIN_COMMUNITY_SIZE
            )
            self.max_community_size = (
                self.max_community_size if self.max_community_size is not None else DEFAULT_MAX_COMMUNITY_SIZE
            )

            if self.beta < 1 or self.beta > 2:
                raise ValueError("beta must be between 1 and 2")

            if self.min_community_size > self.max_community_size:
                raise ValueError("min_community_size must be between min_degree and max_community_size")

            if self.max_community_size > self.vcount - self.num_outliers:
                raise ValueError("max_community_size must be less than n")

        if self.vcount < 1 or not isinstance(self.vcount, int):
            raise ValueError("vcount must be a positive integer")

        if self.xi < 0 or self.xi > 1:
            raise ValueError("xi must be between 0 and 1")

        if self.num_outliers < 0:
            raise ValueError("num_outliers must be non-negative")

        if self.num_outliers > self.vcount:
            raise ValueError("num_outliers must be less than vcount")
