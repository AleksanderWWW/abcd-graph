__all__ = [
    "Model",
    "configuration_model",
    "chung_lu",
]

from typing import Protocol

import numpy as np
from numpy.typing import NDArray


class Model(Protocol):
    def __call__(self, degree_sequence: dict[int, int]) -> NDArray: ...


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

    # Normalize degrees to get the probabilities
    probabilities = normalize(degrees)

    # Total number of stubs (degree volume)
    volume = sum(degrees)

    # Sample nodes according to their degree distribution
    samples = np.random.choice(a=nodes, size=volume, p=probabilities)

    # Initialize adjacency matrix
    num_nodes = len(nodes)
    edges = np.zeros((num_nodes, num_nodes), dtype=np.int64)

    # Form edges
    for i in range(0, volume, 2):
        u = samples[i]
        v = samples[i + 1]
        edges[u, v] += 1
        edges[v, u] += 1

    # Remove self-loops
    np.fill_diagonal(edges, 0)

    # Convert to simple graph (0 or 1 entries)
    edges = np.minimum(edges, 1)

    return edges
