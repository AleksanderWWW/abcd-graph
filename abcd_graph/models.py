from typing import Any, Protocol

import numpy as np
from numba import from_dtype, njit
from numba.typed import List, Set
from numba.types import UniTuple  # type: ignore
from numpy.random import Generator
from numpy.typing import NDArray


class Model(Protocol):
    def __call__(
        self,
        node_ids: NDArray[np.integer[Any]],
        degrees: NDArray[np.integer[Any]],
        rng: Generator,
        out: NDArray[np.integer[Any]] | None = None,
    ) -> NDArray[np.integer[Any]]: ...


def chunglu_model(
    node_ids: NDArray[np.integer[Any]],
    degrees: NDArray[np.integer[Any]],
    rng: Generator,
    out: NDArray[np.integer[Any]] | None = None,
) -> NDArray[np.integer[Any]]:
    """Sample a random graph with, on expectation, the given degree sequence.

    Parameters
    ----------
    node_ids: NDArray[np.integer[Any]]
        List of node_ids for the graph. The returned edge list will contain each
        node_id equal to it's degree

    degrees: NDArray[np.integer[Any]]
        List of degrees. The value degrees[i] corresponds to the degree of node node_ids[i]

    rng: Generator
        numpy.random.Generator object used for randomness.

    out: NDArray[np.integer[Any]] | None (default=None)
        If passed, write output into this array inplace. Can be passed as a view of a larger array.
    """
    sum_degrees = np.sum(degrees)
    node_probs = degrees / sum_degrees
    edges = rng.choice(node_ids, size=(sum_degrees // 2, 2), p=node_probs)
    if out is not None:
        out[:] = edges
    return edges


@njit(nogil=True)
def configuration_model(
    node_ids: NDArray[np.integer[Any]],
    degrees: NDArray[np.integer[Any]],
    rng: Generator,
    out: NDArray[np.integer[Any]] | None = None,
) -> NDArray[np.integer[Any]]:
    """Sample a random graph with the given degree sequence.

    Parameters
    ----------
    node_ids: NDArray[np.integer[Any]]
        List of node_ids for the graph. The returned edge list will contain each
        node_id equal to it's degree

    degrees: NDArray[np.integer[Any]]
        List of degrees. The value degrees[i] corresponds to the degree of node node_ids[i]

    rng: Generator
        numpy.random.Generator object used for randomness.

    out: NDArray[np.integer[Any]] | None (default=None)
        If passed, write output into this array inplace. Can be passed as a view of a larger array.
    """
    n_stubs = np.sum(degrees)
    if out is None:
        out = np.empty((n_stubs // 2, 2), dtype=node_ids.dtype)
    else:
        assert out.shape == (n_stubs // 2, 2)

    next_index = 0
    for node, degree in zip(node_ids, degrees):
        for i in range(next_index, next_index + degree):
            r_i = i if i < out.shape[0] else i - out.shape[0]
            c_i = 0 if i < out.shape[0] else 1
            out[r_i, c_i] = node
        next_index += degree

    # Inplace Fisher-Yates shuffle all elements of 2d array
    n_stubs = out.shape[0] * out.shape[1]
    for i in range(n_stubs):
        i = n_stubs - i - 1
        j = rng.integers(0, i + 1)
        # Map to 2d (row, col) coordinates
        r_i = i if i < out.shape[0] else i - out.shape[0]
        c_i = 0 if i < out.shape[0] else 1
        r_j = j if j < out.shape[0] else j - out.shape[0]
        c_j = 0 if j < out.shape[0] else 1
        # Swap the elements
        temp = out[r_i, c_i]
        out[r_i, c_i] = out[r_j, c_j]
        out[r_j, c_j] = temp

    return out


@njit(inline="always")
def make_edge_tuple(edge) -> tuple[int, int]:
    high, low = edge[0], edge[1]
    if high < low:
        high, low = low, high
    return (low, high)


@njit(inline="always")
def swap(
    edge1: tuple[int, int],
    edge2: tuple[int, int],
    rng: Generator,
) -> tuple[tuple[int, int], tuple[int, int]]:
    if rng.uniform() > 0.5:
        return make_edge_tuple((edge1[0], edge2[0])), make_edge_tuple(
            (edge2[0], edge1[0])
        )
    return make_edge_tuple((edge1[0], edge2[1])), make_edge_tuple((edge1[1], edge2[0]))


@njit(inline="always")
def is_bad_swap(
    edge1: tuple[int, int],
    edge2: tuple[int, int],
    good_edges: Set[tuple[int, int]],
) -> bool:
    if edge1[0] == edge1[1] or edge2[0] == edge2[1]:
        return True
    if edge1 == edge2:
        return True
    if edge1 in good_edges or edge2 in good_edges:
        return True
    return False


def get_edge_type(edges: NDArray[np.integer[Any]]) -> tuple[int, int]:
    return UniTuple(from_dtype(edges.dtype), 2)


@njit(nogil=True)
def rewire(
    edges: NDArray[np.integer[Any]],
    edge_type: tuple[int, int],
    rng: Generator,
    max_swap_attempts_per_bad_edge: int = 5,
    print_info: bool = False,
) -> int:
    """Perform inplace edge swaps to resolve loops and multi-edges.

    Parameters
    ----------

    edges: NDArray[np.integer[Any]]
        Edge list with shape (n_edges, 2) to be rewired. Will be altered in place.

    node_dtype: np.integer[Any]
        dtype of nodes stored in the edges list. Required for numba pre-compilation
        and is assumed to be correct. Consistency checks should be made before
        calling this function.

    rng: Generator
        numpy.random.Generator object to use for randomness.

    max_swap_attempts_per_bad_edge: int, default=5
        Cap the attempted edge swaps to this values times the number of initial bad edges.

    """
    # Move good edges to the front, add their hashes to a set, and
    # make a List-backed-queue of bad edges
    good_edges = Set.empty(edge_type)
    bad_queue = List.empty_list(edge_type)
    n_good_edges = 0
    for i in range(edges.shape[0]):
        edge = make_edge_tuple(edges[i])
        if edge[0] != edge[1] and edge not in good_edges:
            good_edges.add(edge)
            edges[n_good_edges] = edge
            n_good_edges += 1
        else:
            bad_queue.append(edge)

    # Try to resolve the bad edge at the head of bad_queue by trying a swap
    # with a random edge (good or bad, but not the one we are trying to resolve)
    # If the swap would cause a collision, move bad edge to the back of the
    # queue. Repeat until the Queue is empty or we give up.

    if print_info:
        print(len(bad_queue), "bad edges")
        # print(good_edges)
        # print(bad_queue)

    # Store bad edges in the indices 0:queue_len and keep at the front
    # of the list
    next_index = len(bad_queue) - 1
    queue_len = len(bad_queue)

    for _ in range(len(bad_queue) * max_swap_attempts_per_bad_edge):
        if queue_len == 0:
            break

        next_index = (next_index + 1) % queue_len
        bad_edge = bad_queue[next_index]

        # Check if edge is still bad. Conflicting edge may have been switched.
        if bad_edge[0] != bad_edge[1] and bad_edge not in good_edges:
            edges[n_good_edges] = bad_edge
            good_edges.add(bad_edge)
            n_good_edges += 1
            bad_queue[next_index] = bad_queue[queue_len - 1]
            queue_len -= 1
            continue

        choose_from_good_edges = rng.uniform() < n_good_edges / (
            n_good_edges + queue_len - 1
        )  # Always True if queue_len == 1
        if choose_from_good_edges:
            swap_index = rng.integers(0, n_good_edges)
            swap_candidate_edge = make_edge_tuple(edges[swap_index])
            new_edge1, new_edge2 = swap(bad_edge, swap_candidate_edge, rng)
            # if print_info:
            #     print("Try swapping", bad_edge, swap_candidate_edge, "to", new_edge1, new_edge2)
            if not is_bad_swap(new_edge1, new_edge2, good_edges):
                # if print_info:
                #     print("Okay")
                edges[swap_index] = new_edge1
                edges[n_good_edges] = new_edge2
                n_good_edges += 1
                good_edges.add(new_edge1)
                good_edges.add(new_edge2)
                good_edges.discard(swap_candidate_edge)
                bad_queue[next_index] = bad_queue[queue_len - 1]
                queue_len -= 1
        else:
            swap_offset = rng.integers(1, queue_len)  # don't choose current head
            swap_index = (next_index + swap_offset) % queue_len
            swap_candidate_edge = bad_queue[swap_index]
            new_edge1, new_edge2 = swap(bad_edge, swap_candidate_edge, rng)
            # if print_info:
            #     print("Try swapping", bad_edge, swap_candidate_edge, "to", new_edge1, new_edge2)
            if not is_bad_swap(new_edge1, new_edge2, good_edges):
                # if print_info:
                #     print("Okay")
                edges[n_good_edges] = new_edge1
                edges[n_good_edges + 1] = new_edge2
                n_good_edges += 2
                good_edges.add(new_edge1)
                good_edges.add(new_edge2)
                bad_queue[next_index] = bad_queue[queue_len - 1]
                bad_queue[swap_index] = bad_queue[queue_len - 2]
                queue_len -= 2

    # if print_info:
    #     print(edges)
    #     print()
    #     print()
    #     print()

    # Write bad edges that failed to swap back into the edge list
    for i in range(queue_len):
        edges[n_good_edges + i] = bad_queue[i]

    return n_good_edges
