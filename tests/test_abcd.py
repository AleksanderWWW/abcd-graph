import numpy as np
import numpy.testing as npt
import pytest
import scipy.sparse as sp
from utils import assert_no_bad_edges

from abcd_graph import ABCD
from abcd_graph.abcd_sample import ABCDSample


@pytest.mark.parametrize("n", [1000, 2000])
@pytest.mark.parametrize("xi", [0.2, 0.5, 0.7])
def test_abcd(n, xi):
    rng = np.random.default_rng(seed=1)
    abcd = ABCD(n, xi=xi, rng=rng)
    sample = abcd.sample()

    assert_no_bad_edges(sample.edges)
    assert np.max(sample.edges) == n - 1
    assert sample.n == n
    assert np.abs(sample.xi - xi) < 0.15  # xi is noisy


@pytest.mark.benchmark
@pytest.mark.parametrize("n", [1000, 2000])
@pytest.mark.parametrize("xi", [0.2, 0.5, 0.7])
@pytest.mark.parametrize("eta", [1.5, 2.0])
@pytest.mark.parametrize("rho", [0.0, -0.3, 0.3])
def test_abcdoo(n, xi, eta, rho):
    rng = np.random.default_rng(seed=1)
    abcd = ABCD(n, xi=xi, eta=eta, rho=rho, rng=rng)
    sample = abcd.sample()

    assert_no_bad_edges(sample.edges)
    assert np.max(sample.edges) == n - 1
    assert sample.n == n
    assert np.abs(sample.xi - xi) < 0.15  # xi is noisy
    assert sample.eta == eta
    if rho != 0:
        assert np.sign(sample.rho) == np.sign(rho)


@pytest.mark.parametrize(
    "n, dtype",
    [
        (255, np.uint8),
        (256, np.uint16),
    ],
)
def test_abcd_sets_dtype(n, dtype):
    abcd = ABCD(n)
    sample = abcd.sample()
    assert sample.edges.dtype == dtype


@pytest.mark.parametrize("n", [100, 200])
def test_seed(n):
    rng1 = np.random.default_rng(seed=1)
    rng2 = np.random.default_rng(seed=1)

    abcd = ABCD(n, rng=rng1)
    sample1 = abcd.sample()

    # reset seed
    abcd.rng = rng2
    sample2 = abcd.sample()

    assert_no_bad_edges(sample1.edges)
    assert_no_bad_edges(sample2.edges)
    npt.assert_array_equal(sample1.edges, sample2.edges)
    npt.assert_array_equal(sample2.to_dense(), sample2.to_dense())


def test_fit():
    edges = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [1, 3]], dtype=np.uint32)
    coms = sp.csr_array([[1, 1, 1, 0, 0], [0, 0, 1, 1, 0]])
    sample = ABCDSample(edges, coms)
    abcd = ABCD(100)

    abcd.fit(sample)

    assert abcd.n == 5
    assert abcd.xi == 0.5
    assert abcd.eta == 1.25
    assert abcd.min_degree == 2
    assert abcd.max_degree == 3
    assert abcd.degree_exponent != 2.5
    assert abcd.min_community_size == 2
    assert abcd.max_community_size == 3
    assert abcd.community_size_exponent != 1.5
    assert abcd.degree_sequence is None
    assert abcd.community_size_sequence is None


def test_fit_with_sequences():
    edges = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [1, 3]], dtype=np.uint32)
    coms = sp.csr_array([[1, 1, 1, 0, 0], [0, 0, 1, 1, 0]])
    sample = ABCDSample(edges, coms)
    abcd = ABCD(100)

    abcd.fit(sample, do_not_set=None)

    assert abcd.n == 5
    assert abcd.xi == 0.5
    assert abcd.eta == 1.25
    assert abcd.min_degree == 2
    assert abcd.max_degree == 3
    assert abcd.degree_exponent != 2.5
    assert abcd.min_community_size == 2
    assert abcd.max_community_size == 3
    assert abcd.community_size_exponent != 1.5
    npt.assert_array_equal(abcd.degree_sequence, np.array([2, 3, 2, 3, 2]))
    npt.assert_array_equal(abcd.community_size_sequence, np.array([3, 2]))


def test_fit_degree_sequence_but_not_n_raises():
    edges = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [1, 3]], dtype=np.uint32)
    coms = sp.csr_array([[1, 1, 1, 0, 0], [0, 0, 1, 1, 0]])
    sample = ABCDSample(edges, coms)
    abcd = ABCD(100)

    with pytest.raises(ValueError):
        abcd.fit(sample, do_not_set=["n"])
