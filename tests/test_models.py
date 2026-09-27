import numpy as np
import pytest
from utils import assert_no_bad_edges

from abcd_graph.models import chunglu_model, configuration_model, get_edge_type, rewire


def test_chunglu_model():
    rng = np.random.default_rng(seed=1)
    node_ids = np.arange(32, dtype=np.uint32)
    degrees = np.full(32, 4, dtype=np.int64)

    edges = chunglu_model(node_ids, degrees, rng)

    ids, counts = np.unique(edges, return_counts=True)
    assert set(ids).issubset(set(node_ids))
    assert edges.dtype == np.uint32
    assert edges.shape == (64, 2)


def test_chunglu_model_inplace():
    rng = np.random.default_rng(seed=1)
    node_ids = np.arange(32, dtype=np.uint32)
    degrees = np.full(32, 4, dtype=np.int64)
    edges = np.empty((64, 2), dtype=np.uint32)

    chunglu_model(node_ids, degrees, rng)

    ids, counts = np.unique(edges, return_counts=True)
    assert set(ids).issubset(set(node_ids))
    assert edges.dtype == np.uint32
    assert edges.shape == (64, 2)


def test_configuration_model():
    rng = np.random.default_rng(seed=1)
    node_ids = np.arange(32, dtype=np.uint32)
    degrees = np.full(32, 4, dtype=np.int64)

    edges = configuration_model(node_ids, degrees, rng)

    ids, counts = np.unique(edges, return_counts=True)
    assert set(ids) == set(node_ids)
    assert np.all(counts == 4)
    assert edges.dtype == np.uint32
    assert edges.shape == (64, 2)


def test_configuration_model_inplace():
    rng = np.random.default_rng(seed=1)
    node_ids = np.arange(32, dtype=np.uint32)
    degrees = np.full(32, 4, dtype=np.int64)
    edges = np.empty((64, 2), dtype=np.uint32)

    configuration_model(node_ids, degrees, rng, out=edges)

    ids, counts = np.unique(edges, return_counts=True)
    assert set(ids) == set(node_ids)
    assert np.all(counts == 4)
    assert edges.dtype == np.uint32
    assert edges.shape == (64, 2)


def test_rewire_loops():
    rng = np.random.default_rng(seed=1)
    edges = np.array(
        [
            [0, 0],
            [1, 1],
            [2, 2],
            [3, 4],
            [5, 6],
        ],
        dtype=np.uint32,
    )

    n_good_edges = rewire(edges, get_edge_type(edges), rng)

    assert edges.shape == (5, 2)
    assert edges.dtype == np.uint32
    assert_no_bad_edges(edges)
    assert n_good_edges == edges.shape[0]


def test_rewire_multiedges():
    rng = np.random.default_rng(seed=1)
    edges = np.array(
        [
            [0, 1],
            [0, 1],
            [2, 3],
            [2, 3],
        ],
        dtype=np.uint32,
    )

    n_good_edges = rewire(edges, get_edge_type(edges), rng)

    assert edges.shape == (4, 2)
    assert edges.dtype == np.uint32
    assert_no_bad_edges(edges)
    assert n_good_edges == edges.shape[0]


def test_rewire_swap_two_bad_edges():
    rng = np.random.default_rng(seed=1)
    edges = np.array([[0, 0], [1, 2], [1, 2]], dtype=np.uint32)

    n_good_edges = rewire(edges, get_edge_type(edges), rng)

    assert edges.shape == (3, 2)
    assert edges.dtype == np.uint32
    assert_no_bad_edges(edges)
    assert n_good_edges == edges.shape[0]


def test_rewire_many():
    rng = np.random.default_rng(seed=1)
    edges = np.array(
        [[0, 0], [0, 1], [0, 1], [2, 3], [2, 3], [3, 3], [4, 5], [5, 6]],
        dtype=np.uint32,
    )

    n_good_edges = rewire(edges, get_edge_type(edges), rng)

    assert edges.shape == (8, 2)
    assert edges.dtype == np.uint32
    assert_no_bad_edges(edges)
    assert n_good_edges == edges.shape[0]


def test_rewire_is_idempotent():
    # idempotent: applying more than once is the same as applying once
    # i.e. further rewires do nothing.
    rng = np.random.default_rng(seed=1)
    edges = np.array(
        [[0, 0], [0, 1], [0, 1], [2, 3], [2, 3], [3, 3], [4, 5], [5, 6]],
        dtype=np.uint32,
    )

    rewire(edges, get_edge_type(edges), rng)
    first_rewire = edges.copy()
    rewire(edges, get_edge_type(edges), rng)

    np.testing.assert_equal(first_rewire, edges)


def test_rewire_failure():
    rng = np.random.default_rng(seed=1)
    edges = np.array([[0, 0], [0, 1]], dtype=np.uint32)

    n_good_edges = rewire(edges, get_edge_type(edges), rng)

    assert edges.shape == (2, 2)
    assert edges.dtype == np.uint32
    with pytest.raises(AssertionError):
        assert_no_bad_edges(edges)
    assert n_good_edges == 1
