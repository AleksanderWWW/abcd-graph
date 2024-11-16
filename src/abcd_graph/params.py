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


@dataclass
class ABCDParams:
    vcount: int = 1000
    gamma: float = 2.5
    beta: float = 1.5
    xi: float = 0.25
    min_degree: int = 5
    max_degree: int = 30
    min_community_size: int = 20
    max_community_size: int = 250
    num_outliers: int = 0

    def __post_init__(self) -> None:
        if self.vcount < 1 or not isinstance(self.vcount, int):
            raise ValueError("vcount must be a positive integer")

        if self.gamma < 2 or self.gamma > 3:
            raise ValueError("gamma must be between 2 and 3")

        if self.beta < 1 or self.beta > 2:
            raise ValueError("beta must be between 1 and 2")

        if self.xi < 0 or self.xi > 1:
            raise ValueError("xi must be between 0 and 1")

        if self.min_degree < 1 or self.min_degree > self.max_degree:
            raise ValueError("min_degree must be between 1 and max_degree")

        if self.max_degree >= self.max_community_size:
            raise ValueError("max_degree must be less than max_community_size")

        if self.min_community_size < self.min_degree or self.min_community_size > self.max_community_size:
            raise ValueError("min_community_size must be between min_degree and max_community_size")

        if self.num_outliers < 0:
            raise ValueError("num_outliers must be non-negative")

        if self.num_outliers > self.vcount:
            raise ValueError("num_outliers must be less than vcount")

        if self.max_community_size > self.vcount - self.num_outliers:
            raise ValueError("max_community_size must be less than n")
