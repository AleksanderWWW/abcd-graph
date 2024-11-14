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

__all__ = [
    "Model",
    "configuration_model",
    "chung_lu",
]

from typing import Protocol

import numpy as np
from numpy.typing import NDArray


class Model(Protocol):
    def __call__(self, degree_sequence: dict[int, int]) -> NDArray[np.int64]: ...

    @property
    def __name__(self) -> str: ...


def configuration_model(degree_sequence: dict[int, int]) -> NDArray[np.int64]:
    labels = list(degree_sequence.keys())
    counts = list(degree_sequence.values())

    vertices = np.repeat(labels, counts)

    np.random.shuffle(vertices)

    edges = np.array(vertices).reshape(-1, 2)

    return edges


def normalize(degrees: list[int]) -> NDArray[np.float64]:
    """Normalize the degree sequence."""
    degrees_array: NDArray[np.int64] = np.array(degrees)
    norm = degrees_array.sum()
    result: NDArray[np.float64] = np.divide(degrees_array, norm)
    return result


def chung_lu(degree_sequence: dict[int, int]) -> NDArray[np.int64]:
    """Generate a Chung-Lu random graph based on a given degree sequence."""
    nodes = list(degree_sequence.keys())
    degrees = list(degree_sequence.values())

    return np.random.choice(a=nodes, size=int(sum(degrees)), p=normalize(degrees)).reshape(-1, 2)
