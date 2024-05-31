__all__ = [
    "Model",
    "configuration_model",
]

from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from abcd_graph.typing import DegreeSequence


class Model(Protocol):
    def __call__(self, degree_sequence: DegreeSequence) -> NDArray:
        ...


def configuration_model(degree_sequence: DegreeSequence) -> NDArray[np.int64]:
    labels = list(degree_sequence.keys())
    counts = list(degree_sequence.values())

    vertices = np.repeat(labels, counts)

    np.random.shuffle(vertices)

    edges = np.array(vertices).reshape(-1, 2)

    return edges
