from typing import Any

import numpy as np
import scipy.sparse as sp
from numpy.random import Generator
from numpy.typing import NDArray


def make_primary_community_sizes(
    n: int,
    community_sizes: NDArray[np.integer[Any]],
    rng: Generator,
) -> NDArray[np.integer[Any]]:
    n_coms = len(community_sizes)
    # Make primary community sizes with expected size
    # equal to full_size / eta.
    eta = np.sum(community_sizes) / n
    primary_community_sizes = community_sizes / eta
    primary_community_sizes += rng.uniform(size=n_coms)
    primary_community_sizes = primary_community_sizes.astype(np.uint32)
    # Ensure no community has size 0
    primary_community_sizes[primary_community_sizes == 0] += 1
    # Sum of primary community sizes must be n (will be on expectation).
    # Increase or decrease random communities by one (but not to size 0)
    # to make it so.
    primary_size_sum = np.sum(primary_community_sizes)
    required_change = n - int(primary_size_sum)
    if required_change > 0:
        increase_indices = rng.choice(n_coms, size=required_change, replace=False)
        primary_community_sizes[increase_indices] += 1
    elif required_change < 0:
        big_coms = np.where(primary_community_sizes > 1)[0]
        decrease_indices = rng.choice(
            big_coms, size=required_change * -1, replace=False
        )
        primary_community_sizes[decrease_indices] -= 1
    return primary_community_sizes


def make_overlapping_communities(
    n: int,
    community_sizes: NDArray[np.integer[Any]],
    dimension: int,
    rng: Generator,
) -> sp.csr_array:
    primary_community_sizes = make_primary_community_sizes(n, community_sizes, rng)

    # Make random points on hyperball
    direction = rng.standard_normal(size=(n, dimension), dtype=np.float32)
    direction /= np.linalg.norm(direction, axis=1, keepdims=True)
    radii = rng.random(size=(n, 1), dtype=np.float32) ** (1.0 / dimension)
    points = radii * direction

    primary_communities = []
    has_primary = np.zeros(n, dtype=np.bool)
    norms = np.linalg.norm(points, axis=1)
    for size in primary_community_sizes:
        available_ids = np.where(~has_primary)[0]
        seed = np.argmax(norms[available_ids])
        dist_from_seed = np.linalg.norm(points[available_ids] - seed, axis=1)
        community_ids = available_ids[np.argsort(dist_from_seed)[:size]]
        primary_communities.append(community_ids)
        has_primary[community_ids] = True

    # Expand primary communities to full size
    communities = []
    for primary_members, final_size in zip(primary_communities, community_sizes):
        n_new = final_size - len(primary_members)
        non_members = np.setdiff1d(np.arange(n), primary_members)
        community_mean = np.mean(points[primary_members], axis=0)
        dist_to_mean = np.linalg.norm(points[non_members] - community_mean, axis=1)
        new_members = non_members[np.argsort(dist_to_mean)[:n_new]]
        communities.append(np.concatenate((primary_members, new_members)))

    indptr = np.arange(len(community_sizes) + 1)
    indices = np.empty(np.sum(community_sizes), dtype=indptr.dtype)
    next_indptr = 0
    for i, members in enumerate(communities):
        indptr[i] = next_indptr
        indices[next_indptr : next_indptr + len(members)] = members
        next_indptr += len(members)
    indptr[-1] = next_indptr
    data = np.ones_like(indices, dtype=np.bool)
    membership_array = sp.csr_array(
        (data, indices, indptr), shape=(len(community_sizes), n), dtype=np.bool
    )
    return membership_array


def build_membership_matrix(
    n: int,
    community_sizes: NDArray[np.integer[Any]],
    n_outliers: int,
    dimension: int,
    rng: Generator,
) -> sp.csr_array:
    """
    Build a communities x nodes sparse array of community memberships.

    Parameters
    ----------
    n: int
        The number of nodes

    community_sizes: NDArray[np.integer[Any]]
        Array of final community sizes.

    n_outliers: int
        Number of outlier nodes, i.e. no community. These will be assigned
        the higher of node ids.

    dimension: int
        Dimension of geometry for overlapping communities. Not used if eta=1.0.

    rng: Generator
        numpy.random.Generator object used for randomness in the construction
        of overlapping communities. Not used if eta=1.0.
    """
    n_inliers = n - n_outliers
    # eta is average number of communities per non-outlier node, following
    # naming from the ABCDoo paper
    eta = np.sum(community_sizes) / n_inliers
    if eta == 1:
        indptr = np.cumsum(community_sizes)
        indptr = np.insert(indptr, 0, 0)
        indices = np.arange(np.sum(community_sizes), dtype=np.int32)
        data = np.ones_like(indices, dtype=np.bool)
        membership_array = sp.csr_array(
            (data, indices, indptr), shape=(len(community_sizes), n)
        )
        return membership_array

    if eta < 1:
        raise ValueError("eta must be at least 1.")
    if dimension < 1:
        raise ValueError("dimension must be at least 1.")
    membership_matrix = make_overlapping_communities(
        n_inliers,
        community_sizes,
        dimension,
        rng,
    )
    # Add outliers as empty columns on the right
    membership_matrix._shape = (len(community_sizes), n)
    return membership_matrix
