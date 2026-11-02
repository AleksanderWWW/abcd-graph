import numpy as np
import numpy.testing as npt
import pytest
import scipy.sparse as sp

from abcd_graph.abcd_sample import ABCDSample


@pytest.fixture
def sample():
    edges = np.array([[0, 1], [1, 2], [2, 3], [3, 4]], dtype=np.uint32)
    membership_matrix = sp.csr_array([[1, 1, 0, 0, 0], [0, 1, 1, 1, 0]], dtype=np.bool)
    sample = ABCDSample(edges, membership_matrix)
    return sample


def test_xi(sample):
    xi = sample.xi
    assert xi == 0.25


@pytest.mark.filterwarnings("ignore::UserWarning:powerlaw*")
def test_degree_exponent(sample):
    exponent = sample.degree_exponent
    assert exponent > 0


@pytest.mark.filterwarnings("ignore::UserWarning:powerlaw*")
def test_community_size_exponent(sample):
    exponent = sample.community_size_exponent
    assert exponent > 0


def test_to_sparse(sample):
    result = sample.to_sparse()
    correct = sp.csr_array(
        [
            [0, 1, 0, 0, 0],
            [1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [0, 0, 0, 1, 0],
        ],
        dtype=np.bool,
    )

    npt.assert_array_equal(correct.todense(), result.todense())
    assert isinstance(result, sp.csr_array)


def test_to_sparse_matrix(sample):
    assert isinstance(sample.to_sparse(matrix=True), sp.csr_matrix)


def test_to_dense(sample):
    result = sample.to_dense()
    correct = np.array(
        [
            [0, 1, 0, 0, 0],
            [1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [0, 0, 0, 1, 0],
        ],
        dtype=np.bool,
    )

    npt.assert_array_equal(correct, result)


def test_to_networkx(sample):
    pytest.importorskip("networkx")
    result = sample.to_networkx()

    assert result.number_of_nodes() == 5
    assert result.number_of_edges() == 4


def test_to_igraph(sample):
    pytest.importorskip("igraph")
    result = sample.to_igraph()

    assert result.vcount() == 5
    assert result.ecount() == 4


def test_community_array(sample):
    sample.membership_matrix = sp.csr_array(
        [[1, 1, 0, 0, 0], [0, 0, 1, 1, 0]], dtype=np.bool
    )
    result = sample.community_array

    correct = np.array([0, 0, 1, 1, -1])
    npt.assert_array_equal(correct, result)


def test_community_array_raises_with_overlap(sample):
    with pytest.raises(ValueError):
        result = sample.community_array
        assert len(result) == 5
