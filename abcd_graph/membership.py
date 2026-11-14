from typing import Any

import numpy as np
import scipy.sparse as sp
from numba import njit
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


@njit(fastmath=True, cache=True)
def assign_overlapping_communities_with_reference_layer(
    points: NDArray[np.float32],
    radii: NDArray[np.float32],
    primary_sizes: NDArray[np.integer[Any]],
    community_sizes: NDArray[np.integer[Any]],
):
    n, dim = points.shape
    n_coms = len(community_sizes)
    total_memberships = np.sum(community_sizes)

    # Build final csr data structure directly
    indptr = np.empty(n_coms + 1, dtype=np.int64)
    indices = np.empty(total_memberships, dtype=np.int64)
    next_indptr = 0

    # Pre-allocate intermediate arrays
    has_primary = np.zeros(n, dtype=np.bool)
    in_current_com = np.zeros(n, dtype=np.bool)
    dists = np.empty(n, dtype=np.float32)

    for com_id in range(n_coms):
        # (1) Compute primary community
        n_primary = primary_sizes[com_id]

        # (1a) Find seed
        seed = -1
        seed_norm = np.float32(np.inf)
        for i in range(n):
            if not has_primary[i] and radii[i] > seed_norm:
                seed = i
                seed_norm = radii[i]
        seed_point = points[seed]

        # (1b) Compute dists of all non-assigned points to seed
        # set those already assigned to np.inf so sorting
        # by closest to seed puts them last
        for i in range(n):
            if has_primary[i]:
                dists[i] = np.inf
            else:
                dists[i] = np.sum((points[i] - seed_point) ** 2)
        # (1c) get ids closest to seed
        primary_members = np.argpartition(dists, n_primary - 1)[:n_primary]
        has_primary[primary_members] = True

        # (2) Expand community around center
        n_secondary = community_sizes[com_id] - n_primary
        secondary_members = np.empty(
            0, dtype=primary_members.dtype
        )  # in case we don't expand
        if n_secondary > 0:
            # (2a) compute center
            center = np.zeros(dim, dtype=np.float32)
            for point_id in primary_members:
                center += points[point_id]
            center *= 1 / n_primary

            # (2b) compute distance of points not already in the
            # community to the mean
            in_current_com[:] = False
            in_current_com[primary_members] = True
            for i in range(n):
                if in_current_com[i]:
                    dists[i] = np.inf
                else:
                    dists[i] = np.sum((points[i] - center) ** 2)
            # (2c) get ids closest to mean
            secondary_members = np.argpartition(dists, n_secondary - 1)[:n_secondary]

        # (3) record members
        members = np.hstack((primary_members, secondary_members))
        members = np.sort(members)
        indptr[com_id] = next_indptr
        indices[next_indptr : next_indptr + len(members)] = members
        next_indptr += len(members)

    indptr[-1] = next_indptr
    return indptr, indices


def make_overlapping_communities(
    n: int,
    final_community_sizes: NDArray[np.integer[Any]],
    dimension: int,
    rng: Generator,
) -> sp.csr_array:
    primary_community_sizes = make_primary_community_sizes(
        n, final_community_sizes, rng
    )

    # Make random points on hyperball
    direction = rng.standard_normal(size=(n, dimension), dtype=np.float32)
    direction /= np.linalg.norm(direction, axis=1, keepdims=True)
    radii = rng.random(size=(n, 1), dtype=np.float32) ** (1.0 / dimension)
    points = radii * direction
    radii = radii.reshape(
        -1
    )  # Remove extra dimension used to make the above multiplication work

    indptr, indices = assign_overlapping_communities_with_reference_layer(
        points, radii, primary_community_sizes, final_community_sizes
    )

    data = np.ones_like(indices, dtype=np.bool)
    membership_array = sp.csr_array(
        (data, indices, indptr), shape=(len(final_community_sizes), n), dtype=np.bool
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
