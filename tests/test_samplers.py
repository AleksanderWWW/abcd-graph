import numpy as np
import pytest

from abcd_graph.samplers import (
    fix_community_sizes,
    sample_community_sizes,
    sample_degrees,
)


@pytest.mark.parametrize("n", [20, 25])
def test_sample_degrees(n):
    exponent = 2.5
    min_degree = 3
    max_degree = 5
    rng = np.random.default_rng(seed=1)

    degrees = sample_degrees(n, exponent, min_degree, max_degree, rng)

    assert degrees.shape == (n,)
    assert set(degrees).issubset(set(range(min_degree, max_degree + 1)))


def test_fix_community_sizes_decrease_last():
    community_sizes = np.array([10, 10, 10])
    target_sum = 25
    min_community_size = 3
    max_community_size = 15
    rng = np.random.default_rng(seed=1)  # Not used but must be passed

    fixed_sizes = fix_community_sizes(
        community_sizes, target_sum, min_community_size, max_community_size, rng
    )

    assert np.all(np.array([10, 10, 5]) == fixed_sizes)


def test_fix_community_sizes_increase_random():
    community_sizes = np.array([12, 12, 4])
    target_sum = 25
    min_community_size = 3
    max_community_size = 15
    rng = np.random.default_rng(seed=1)

    fixed_sizes = fix_community_sizes(
        community_sizes, target_sum, min_community_size, max_community_size, rng
    )

    assert 12 in fixed_sizes
    assert 13 in fixed_sizes
    assert len(fixed_sizes) == 2
    assert np.sum(fixed_sizes) == target_sum


@pytest.mark.parametrize("n", [20, 25])
@pytest.mark.parametrize("eta", [1.0, 1.5])
def test_sample_community_sizes_no_overlap(n, eta):
    exponent = 1.5
    min_community_size = 3
    max_community_size = 10
    rng = np.random.default_rng(seed=1)

    community_sizes = sample_community_sizes(
        n, exponent, min_community_size, max_community_size, eta, rng
    )

    min_n_communities = n * eta / max_community_size
    max_n_communities = n * eta / min_community_size
    assert len(community_sizes) >= min_n_communities
    assert len(community_sizes) <= max_n_communities
    assert set(community_sizes).issubset(
        set(range(min_community_size, max_community_size + 1))
    )
    assert np.abs(np.sum(community_sizes) - n * eta) < 1
