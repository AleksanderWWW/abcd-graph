import numpy as np
import pytest

from abcd_graph.membership import (
    build_membership_matrix,
    make_primary_community_sizes,
)


@pytest.mark.parametrize("n", [20, 25])
def test_primary_community_sizes(n):
    community_sizes = np.array([10, 10, 10])
    rng = np.random.default_rng(seed=1)

    primary_community_sizes = make_primary_community_sizes(n, community_sizes, rng)

    expected_values = community_sizes / (np.sum(community_sizes) / n)
    assert np.max(np.abs(primary_community_sizes - expected_values)) < 1
    assert np.sum(primary_community_sizes) == n
    assert primary_community_sizes.dtype == np.uint32


def test_no_zero_primary_community_sizes():
    n = 20
    community_sizes = np.array([10, 10, 10, 1])
    rng = np.random.default_rng(seed=1)

    primary_community_sizes = make_primary_community_sizes(n, community_sizes, rng)

    expected_values = community_sizes / (np.sum(community_sizes) / n)
    assert np.max(np.abs(primary_community_sizes - expected_values)) < 1
    assert np.sum(primary_community_sizes) == n
    assert primary_community_sizes.dtype == np.uint32
    assert np.all(primary_community_sizes > 0)


@pytest.mark.parametrize("n", [20, 25])
@pytest.mark.parametrize("n_out", [3, 5])
def test_build_membership_matrix(n, n_out):
    community_sizes = np.array([5, n - n_out - 5])
    dimension = 2
    rng = np.random.default_rng(seed=1)

    membership_array = build_membership_matrix(
        n, community_sizes, n_out, dimension, rng
    )

    assert membership_array.shape == (len(community_sizes), n)
    assert np.all(membership_array.sum(axis=1) == community_sizes)
    n_coms = membership_array.sum(axis=0)
    assert np.all(n_coms[: n - n_out] == 1)
    assert np.all(n_coms[n - n_out :] == 0)
    assert np.all(membership_array.data == 1)


@pytest.mark.parametrize("n", [20, 25])
@pytest.mark.parametrize("n_out", [3, 5])
@pytest.mark.parametrize("dimension", [2, 4])
def test_build_overlapping_membership_matrix(n, n_out, dimension):
    community_sizes = np.array([10, 10, 10])
    rng = np.random.default_rng(seed=1)

    membership_array = build_membership_matrix(
        n, community_sizes, n_out, dimension, rng
    )

    assert membership_array.shape == (len(community_sizes), n)
    assert np.all(membership_array.sum(axis=1) == community_sizes)
    n_coms = membership_array.sum(axis=0)
    assert np.all(n_coms[: n - n_out] >= 1)
    assert np.all(n_coms[n - n_out :] == 0)
    assert np.all(membership_array.data == 1)
