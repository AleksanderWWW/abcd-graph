from typing import Any

import numpy as np
from numba import njit
from numpy.random import Generator
from numpy.typing import DTypeLike, NDArray


def sample_degrees(
    n: int,
    degree_exponent: float,
    min_degree: int,
    max_degree: int,
    rng: Generator,
    dtype: DTypeLike | None = None,
) -> NDArray[np.integer[Any]]:
    dtype = dtype if dtype is not None else np.min_scalar_type(n)
    options = np.arange(min_degree, max_degree + 1, dtype=dtype)
    probs = options.astype(np.float32) ** -degree_exponent
    probs /= np.sum(probs)
    degrees = rng.choice(options, p=probs, size=n)
    if np.sum(degrees) % 2 == 1:
        max_indices = np.where(degrees == np.max(degrees))[0]
        index_to_decrease = rng.choice(max_indices)
        degrees[index_to_decrease] -= 1
    return degrees


@njit
def _sample_community_sizes(
    available_sizes: NDArray[np.integer[Any]],
    probs: NDArray[np.float32],
    target_sum: float,
    rng: Generator,
):
    max_n_communities = int(np.ceil(target_sum / available_sizes[0]))
    community_sizes = np.empty(max_n_communities, dtype=available_sizes.dtype)
    prob_cumsum = np.cumsum(probs)
    next_id = 0
    sizes_sum = 0
    for i in range(len(community_sizes)):
        random = rng.uniform()
        index = np.searchsorted(prob_cumsum, random)
        size = available_sizes[index]
        community_sizes[i] = size
        next_id += 1
        sizes_sum += size
        if sizes_sum > target_sum - 1:
            break

    return community_sizes[:next_id].copy()  # Copy to free memory


def fix_community_sizes(
    community_sizes: NDArray[np.integer[Any]],
    target_sum: float,
    min_community_size: int,
    max_community_size: int,
    rng: Generator,
):
    sizes_sum = np.sum(community_sizes)
    if sizes_sum - target_sum >= 1:
        # rand round target_sum up or down
        target_sum = int(target_sum + rng.uniform())
        decrease_amount = int(sizes_sum - target_sum)
        if community_sizes[-1] >= decrease_amount + min_community_size:
            community_sizes[-1] -= decrease_amount
        else:
            increase_amount = community_sizes[-1] - decrease_amount
            community_sizes = community_sizes[:-1]
            while increase_amount > 0:
                increasable_indices = np.where(community_sizes < max_community_size)[0]
                if len(increasable_indices) == 0:
                    raise ValueError(
                        "Stuck fixing community sizes. This is likely caused by a too large min_community_size."
                    )
                n_to_increase = min(increase_amount, len(increasable_indices))
                indices_to_increase = rng.choice(
                    increasable_indices, size=n_to_increase, replace=False
                )
                community_sizes[indices_to_increase] += 1
                increase_amount -= n_to_increase

    return community_sizes


def sample_community_sizes(
    n: int,
    community_size_exponent: float,
    min_community_size: int,
    max_community_size: int,
    eta: float,
    rng: Generator,
    dtype: DTypeLike | None = None,
) -> NDArray[np.integer[Any]]:
    dtype = dtype if dtype is not None else np.min_scalar_type(n)
    target_sum = n * eta
    options = np.arange(min_community_size, max_community_size + 1, dtype=dtype)
    probs = options.astype(np.float32) ** -community_size_exponent
    probs /= np.sum(probs)

    community_sizes = _sample_community_sizes(
        options,
        probs,
        target_sum,
        rng,
    )

    community_sizes = fix_community_sizes(
        community_sizes, target_sum, min_community_size, max_community_size, rng
    )

    return community_sizes
