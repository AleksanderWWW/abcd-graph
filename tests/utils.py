import numpy as np
import scipy.sparse as sp
from numpy.typing import NDArray


def assert_no_bad_edges(edges: NDArray[np.uint32]):
    n = np.max(edges) + 1
    adjacency_matrix = sp.coo_array(
        (np.ones(edges.shape[0], dtype=np.int32), edges.T),
        shape=(n, n),
    )
    assert np.all(adjacency_matrix.diagonal() == 0)
    assert np.all(adjacency_matrix.data == 1)
