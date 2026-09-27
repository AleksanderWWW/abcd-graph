import logging
import sys
from collections.abc import Callable, Container
from time import perf_counter
from typing import Any
from warnings import warn

import numpy as np
import scipy.sparse as sp
from numpy.random import Generator
from numpy.typing import ArrayLike, DTypeLike, NDArray
from tqdm import trange

from abcd_graph.abcd_sample import ABCDSample, icdf
from abcd_graph.degrees import assign_degrees, split_degrees
from abcd_graph.membership import build_membership_matrix
from abcd_graph.models import (
    Model,
    chunglu_model,
    configuration_model,
    get_edge_type,
    rewire,
)
from abcd_graph.samplers import sample_community_sizes, sample_degrees


class TqdmToLogger:
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level
        self.buf = ""

    def write(self, buf):
        self.buf = buf.strip("\r\n")
        if self.buf:
            self.logger.log(self.level, self.buf)

    def flush(self):
        pass


def format_duration(seconds: float):
    if seconds >= 1.0:
        return f"{seconds:.3f}s"
    elif seconds >= 1e-3:
        return f"{seconds * 1e3:.3f}ms"
    elif seconds >= 1e-6:
        return f"{seconds * 1e6:.3f}µs"
    else:
        return f"{seconds * 1e9:.3f}ns"


def generate_graph(
    community_degrees: sp.csr_array,
    background_degrees: NDArray[np.integer[Any]],
    model: Model,
    max_swap_attempts_per_bad_edge: int,
    rng: Generator,
    logger: logging.Logger,
    dtype: DTypeLike,
):
    # Add background degrees as the last community
    community_degrees = sp.vstack(
        (community_degrees, sp.csr_array(background_degrees)), format="csr"
    )
    # Make indptr for edges in each community
    community_m = community_degrees.sum(axis=1) // 2
    community_edges_indptr = np.cumsum(community_m)
    community_edges_indptr = np.insert(community_edges_indptr, 0, 0)

    graph = np.empty((community_edges_indptr[-1], 2), dtype=dtype)
    indices_as_node_ids = community_degrees.indices.astype(dtype)

    logger.info("Building Community Graphs")
    start = perf_counter()
    # TODO Parallel this loop
    tqdm_out = TqdmToLogger(logger, level=logging.INFO)
    for i in trange(community_degrees.shape[0], file=tqdm_out):
        com_nodes = indices_as_node_ids[
            community_degrees.indptr[i] : community_degrees.indptr[i + 1]
        ]
        com_degrees = community_degrees.data[
            community_degrees.indptr[i] : community_degrees.indptr[i + 1]
        ]
        com_graph = graph[community_edges_indptr[i] : community_edges_indptr[i + 1]]
        model(com_nodes, com_degrees, rng, out=com_graph)
        rewire(
            com_graph,
            get_edge_type(com_graph),
            rng,
            max_swap_attempts_per_bad_edge,
        )
    end = perf_counter()
    logger.info(f"Finished in {format_duration(end - start)}.")
    logger.info("Global Rewiring")
    start = perf_counter()
    n_good_edges = rewire(
        graph, get_edge_type(graph), rng, max_swap_attempts_per_bad_edge
    )
    end = perf_counter()
    logger.info(f"Finished in {format_duration(end - start)}.")
    if graph.shape[0] - n_good_edges:
        logger.info(
            f"Failed to rewire {graph.shape[0] - n_good_edges}, they will be removed."
        )
        graph = np.resize(graph[:n_good_edges, :], (n_good_edges, graph.shape[1]))

    return graph


class ABCD:
    """Artificial Benchmark for Community Detection

    This class combines the ABCDGraph and ABCDParams class, essentially adding a
    sample method to ABCDParams.

    Parameters
    ----------
    n : int
        The number of vertices in the graph.

    xi: float, default=0.25
        Proportion of edges in the global background graph. Setting xi=0 gives
        disjoint communities while xi=1 gives a random graph with no community
        structure.

    outliers : int | float, default=0
        Number or proportion of outliers. Outliers have their entire degree in
        the background graph and do not belong to any community.

    eta: float, default=1.0
        Average number of communities for non-outlier nodes. When eta=1 there
        is no overlap.

    dimension: int, default=8
        Dimension of the hidden reference layer used to construct overlapping
        communities. Not used if eta is 1.

    rho: float, default=0,
        Pearson correlation between node degree and the number of communities
        it is in. Not used if eta is 1.

    degree_exponent : float, default=2.5
        Powerlaw exponent for the degree distribution. Not used if
        degree_sequence is passed.

    min_degree : int,  default=5
        Minimum degree in the graph. Not used if degree_sequence is passed.

    max_degree : int | Callable[[int], int], default=int(n**0.5)
        Maximum degree in the graph. May be be passed as a function that
        will be called on n. Not used if degree_sequence is passed.

    community_size_exponent: float, default=1.5
        Powerlaw exponent for the community size distribution. Not used if a
        custom community_size_sequence is passed.

    min_community_size : int, default=20
        Minimum community size. Not used if a custom community_size_sequence
        is passed.

    max_community_size: int | Callable[[int], int], default=int(n**0.75)
        Maximum community size. May be be passed as a function that will be called
        on n. Not used if a custom community_size_sequence is passed.

    degree_sequence : Sequence[int] | NDArray[np.int64] | None, default=None
        Used to pass a custom degree sequence that overrides the default
        powerlaw distribution.

    community_size_sequence : Sequence[int] | NDArray[np.int64] | None, default=None
        Used to pass a custom community size sequence that overrides the default
        powerlaw distribution. The sum of the community sizes must equal the number
        of vertices minus the number of outliers.

    rho_tol: float, default=0.05
        Tolerance for rho optimiziation. Only used if rho is not 0.

    alpha_min: float, default=-60.0
        Minimum bound in rho optimization.  Only used if rho is not 0.

    alpha_max: float, default=60.0
        Maximum bound in rho optimization.  Only used if rho is not 0.

    alpha_iters: int, default=10
        Number of alphas to try in rho optimization.  Only used if rho is not 0.

    model : Model | None, default=None
        Random graph model used to sample the community and background graphs.

    max_swap_attempts_per_bad_edge: int, default=5
        Maximum number of time to try and swap each bad edge during rewiring step.
        Small numbers will improve speed, but degrades the quality since any edges
        that fail to get rewired are dropped.

    rng : numpy.random.Generator, default=numpy.random.default_rng()
        Source of all randomness.

    logger : Logger | None, default=None
        Option to pass a custom logging object.

    verbose : bool, default=False
        Only used if logger is not passed. If True, sets the logger level to info and the
        output to stdout. If False, sets the logger level to warning and the output to
        stderr.
    """

    def __init__(
        self,
        n: int,
        xi: float = 0.25,
        outliers: int | float = 0,
        eta: float = 1.0,
        dimension: int = 8,
        rho: float = 0.0,
        degree_exponent: float = 2.5,
        min_degree: int = 5,
        max_degree: int | Callable[[int], int] = lambda n: int(n**0.5),
        community_size_exponent: float = 1.5,
        min_community_size: int = 20,
        max_community_size: int | Callable[[int], int] = lambda n: int(n**0.75),
        degree_sequence: ArrayLike | None = None,
        community_size_sequence: ArrayLike | None = None,
        rho_tol: float = 0.05,
        alpha_min: float = -60.0,
        alpha_max: float = 60.0,
        alpha_iters: int = 10,
        model: str = "configuration",
        max_swap_attempts_per_bad_edge: int = 5,
        rng: Generator = np.random.default_rng(),
        logger: logging.Logger | None = None,
        verbose: bool = False,
    ):
        self.n = n
        self.xi = xi
        self.outliers = outliers
        self.eta = eta
        self.dimension = dimension
        self.rho = rho
        self.degree_exponent = degree_exponent
        self.min_degree = min_degree
        self.max_degree = max_degree
        self.community_size_exponent = community_size_exponent
        self.min_community_size = min_community_size
        self.max_community_size = max_community_size
        self.degree_sequence = degree_sequence
        self.community_size_sequence = community_size_sequence
        self.alpha_max = alpha_max
        self.alpha_min = alpha_min
        self.alpha_iters = alpha_iters
        self.rho_tol = rho_tol
        self.model = model
        self.max_swap_attempts_per_bad_edge = max_swap_attempts_per_bad_edge
        self.rng = rng
        self.logger = logger
        self.verbose = verbose

    def _validate_params(self):
        if not isinstance(self.n, (int, np.integer)) or self.n < 1:
            raise ValueError("n must be a positive integer")

        if not isinstance(self.xi, (float, np.floating)) or self.xi < 0 or self.xi > 1:
            raise ValueError("xi must be a float between 0 and 1")

        if isinstance(self.outliers, (int, np.integer)):
            if self.outliers < 0 or self.outliers > self.n:
                raise ValueError("integer outliers must be positive and at most n")
        elif isinstance(self.outliers, (float, np.floating)):
            if self.outliers < 0 or self.outliers > 1:
                raise ValueError("float outliers must be between 0 and 1")
        else:
            raise ValueError(
                "outliers must be a positive integer or a float between 0 and 1"
            )

        if not isinstance(self.eta, (float, np.floating)) or self.eta < 1:
            raise ValueError("eta must be at least 1")

        if not isinstance(self.dimension, (int, np.integer)) or self.dimension < 1:
            raise ValueError("dimensions must be a positive integer")

        if (
            not isinstance(self.rho, (float, np.floating))
            or self.rho < -1
            or self.rho > 1
        ):
            raise ValueError("rho must be between -1 and 1")

        if self.degree_sequence is None:
            if (
                not isinstance(self.degree_exponent, (float, np.floating))
                or self.degree_exponent < 0
            ):
                raise ValueError("degree exponent must be positive")
            elif self.degree_exponent < 2 or self.degree_exponent > 3:
                warn(
                    f"Typical degree exponents are between 2 and 3, got {self.degree_exponent}",
                    stacklevel=2,
                )

            if (
                not isinstance(self.min_degree, (int, np.integer))
                or self.min_degree < 1
                or self.min_degree >= self.n
            ):
                raise ValueError("min degree must be a positive int at most n")

            if not isinstance(self.max_degree, Callable) and (
                not isinstance(self.max_degree, (int, np.integer))
                or self.max_degree >= self.n
            ):
                raise ValueError(
                    "max degree must be greater than min degree and less than n"
                )
        else:
            try:
                self.degree_sequence_ = np.asarray(
                    self.degree_sequence, dtype=np.uint32
                )
            except TypeError as e:
                raise ValueError(
                    "degree sequence must be able to cast to a numpy array of uint32"
                ) from e
            if self.degree_sequence_.shape != (self.n,):
                raise ValueError("degree sequence must be 1d array of length n")
            if np.sum(self.degree_sequence_) % 2 != 0:
                raise ValueError("sum of degree sequence must be even")

        if self.community_size_sequence is None:
            if (
                not isinstance(self.community_size_exponent, (float, np.floating))
                or self.community_size_exponent < 0
            ):
                raise ValueError("rho must be positive")
            elif self.community_size_exponent < 1 or self.community_size_exponent > 2:
                warn(
                    f"Typical degree exponents are between 1 and 2, got {self.community_size_exponent}",
                    stacklevel=2,
                )

            if (
                not isinstance(self.min_community_size, (int, np.integer))
                or self.min_community_size < 2
                or self.min_community_size >= self.n
            ):
                raise ValueError(
                    "min community size must be an integer between 2 and n"
                )

            if not isinstance(self.max_community_size, Callable) and (
                not isinstance(self.max_community_size, (int, np.integer))
                or self.max_community_size >= self.n
            ):
                raise ValueError(
                    "max community size must be greater than min community size and less than n"
                )
        else:
            try:
                self.community_size_sequence_ = np.asarray(
                    self.community_size_sequence, dtype=np.uint32
                )
            except TypeError as e:
                raise ValueError(
                    "community size sequence must be able to cast to a numpy array of uint32"
                ) from e
            if np.any(self.community_size_sequence_ >= self.n):
                raise ValueError("community sizes must be less than n")
            if np.any(self.community_size_sequence_ < 1):
                raise ValueError("community sizes must be at least 2")

        if not isinstance(self.alpha_max, (float, np.floating)) or self.alpha_max <= 0:
            raise ValueError("alpha max must be positive")

        if not isinstance(self.alpha_min, (float, np.floating)) or self.alpha_min >= 0:
            raise ValueError("alpha min must be negative")

        if not isinstance(self.alpha_iters, (int, np.integer)) or self.alpha_iters < 1:
            raise ValueError("alpha iters must be positive integer")

        if not isinstance(self.rho_tol, (float, np.floating)) or self.rho_tol < 0:
            raise ValueError("rho tol must be at least 0")

        # TODO models
        if self.model not in ["configuration", "chung-lu"]:
            raise ValueError("model must be one of 'configuration' or 'chung-lu'")

        if (
            not isinstance(self.max_swap_attempts_per_bad_edge, (int, np.integer))
            or self.max_swap_attempts_per_bad_edge < 1
        ):
            raise ValueError(
                "max swap attempts per bad edge must a be positive integer"
            )

        if not isinstance(self.rng, np.random.Generator):
            raise ValueError("rng must be a numpy.random.Generator object")

        if self.logger is not None and not isinstance(self.logger, logging.Logger):
            raise ValueError("logger must be None or a logging.Logger object")

    def _get_logger(self):
        if self.logger is not None:
            return self.logger
        logger = logging.getLogger(__name__)
        logger.handlers.clear()
        if self.verbose:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler(sys.stdout)
            logger.addHandler(handler)
        else:
            logger.setLevel(logging.WARNING)
            handler = logging.StreamHandler(sys.stderr)
            logger.addHandler(handler)
        return logger

    def _get_max_degree(self) -> int:
        if isinstance(self.max_degree, (int, np.integer)):
            return int(self.max_degree)
        return self.max_degree(self.n)

    def _get_max_community_size(self) -> int:
        if isinstance(self.max_community_size, (int, np.integer)):
            return int(self.max_community_size)
        return self.max_community_size(self.n)

    def sample(self) -> ABCDSample:
        sample_start = perf_counter()

        self._validate_params()
        self.logger_ = self._get_logger()

        if self.outliers < 1:
            n_outliers = int(self.n * self.outliers)
        else:
            n_outliers = int(self.outliers)

        self.dtype_ = np.min_scalar_type(self.n)

        if self.degree_sequence is not None:
            degree_sequence = np.asarray(self.degree_sequence, dtype=self.dtype_)
        else:
            self.logger_.info("Generating Degree Sequence")
            start = perf_counter()
            degree_sequence = sample_degrees(
                self.n,
                self.degree_exponent,
                self.min_degree,
                self._get_max_degree(),
                self.rng,
                self.dtype_,
            )
            end = perf_counter()
            self.logger_.info(f"Finished in {format_duration(end - start)}.")

        if self.community_size_sequence is not None:
            community_size_sequence = np.asarray(
                self.community_size_sequence, dtype=self.dtype_
            )
        else:
            self.logger_.info("Generating Degree Sequence")
            start = perf_counter()
            community_size_sequence = sample_community_sizes(
                self.n - n_outliers,
                self.community_size_exponent,
                self.min_community_size,
                self._get_max_community_size(),
                self.eta,
                self.rng,
                self.dtype_,
            )
            end = perf_counter()
            self.logger_.info(f"Finished in {format_duration(end - start)}.")

        self.logger_.info("Building Membership Matrix")
        start = perf_counter()
        membership_matrix = build_membership_matrix(
            self.n,
            community_size_sequence,
            n_outliers,
            self.dimension,
            self.rng,
        )
        end = perf_counter()
        self.logger_.info(f"Finished in {format_duration(end - start)}.")

        self.logger_.info("Assigning Degrees")
        start = perf_counter()
        assigned_degrees = assign_degrees(
            degree_sequence,
            membership_matrix,
            self.xi,
            self.rng,
            self.rho,
            self.rho_tol,
            self.alpha_min,
            self.alpha_max,
            self.alpha_iters,
        )
        end = perf_counter()
        self.logger_.info(f"Finished in {format_duration(end - start)}.")

        self.logger_.info("Splitting Degrees")
        start = perf_counter()
        community_degrees, background_degrees = split_degrees(
            assigned_degrees,
            membership_matrix,
            self.xi,
            self.rng,
        )
        end = perf_counter()
        self.logger_.info(f"Finished in {format_duration(end - start)}.")

        if self.model == "configuration":
            model_func = configuration_model
        elif self.model == "chung-lu":
            model_func = chunglu_model
        else:
            raise ValueError("model should be one of 'configuration' or 'chung-lu")

        graph = generate_graph(
            community_degrees,
            background_degrees,
            model_func,
            self.max_swap_attempts_per_bad_edge,
            self.rng,
            self.logger_,
            self.dtype_,
        )
        sample_end = perf_counter()
        self.logger_.info(
            f"Sampled ABCD graph in {format_duration(sample_end - sample_start)}."
        )
        sample = ABCDSample(graph, membership_matrix)
        return sample

    def fit(
        self,
        graph: ABCDSample,
        do_not_set: Container | None = {"degree_sequence", "community_size_sequence"},
    ):
        """Set parameters of this ABCD class to the empirical values from another graph.
        Measurable parameters are:

            * n
            * xi
            * outliers
            * eta
            * rho
            * degree_exponent
            * min_degree
            * max_degree
            * community_size_exponent
            * min_community_size
            * max_community_size
            * degree_sequence
            * community_size_sequence

        Parameters
        ----------
        graph:ABCDSample
            The graph used to measure empirical values

        do_not_set:Container | None (default={'degree_sequence', 'community_size_sequence'})
            List of parameter names that should not be set to the empirical values. Setting degree
            sequence or community size sequence take priority and force samples to have exactly
            the same sequence.
        """
        # Some combination of parameter must or must not be set together
        if do_not_set is not None:
            if "degree_sequence" not in do_not_set and "n" in do_not_set:
                raise ValueError(
                    """Can not fit degree sequence but not n. Either add 'degree_sequence' or remove 'n'
                    from do_not_set."""
                )

            if "community_size_sequence" not in do_not_set and (
                "n" in do_not_set or "outliers" in do_not_set or "eta" in do_not_set
            ):
                warn(
                    """Fitting community_size_sequence but not 'n', 'outliers', or 'eta' is not well
                    tested, consider fitting all.""",
                    stacklevel=2,
                )

        parameters = [
            "n",
            "xi",
            "outliers",
            "eta",
            "rho",
            "degree_exponent",
            "min_degree",
            "max_degree",
            "community_size_exponent",
            "min_community_size",
            "max_community_size",
            "degree_sequence",
            "community_size_sequence",
        ]
        for parameter in parameters:
            if do_not_set is None or parameter not in do_not_set:
                value = getattr(graph, parameter)
                setattr(self, parameter, value)
        return self

    def expected_degree_icdf(self, points: ArrayLike):
        """Measure the expected inverse cumulative distribution function
        (icdf) of the degree distribution at a sequence of values.

        Parameters
        ----------
        points: ArrayLike
            An array of points at which to measure the icdf. Points must
            be non-negative and increasing.

        Returns
        -------
        NDArray[np.floating]
            The expected icdf values.
        """
        self._validate_params()
        if self.degree_sequence is not None:
            return icdf(points, self.degree_sequence)
        values = np.arange(self.min_degree, self._get_max_degree() + 1)
        weights = values**-self.degree_exponent
        return icdf(points, values, weights=weights)

    def expected_community_size_icdf(self, points: ArrayLike):
        """Measure the expected inverse cumulative distribution function
        (icdf) of the community size distribution at a sequence of values.

        Parameters
        ----------
        points: ArrayLike
            An array of points at which to measure the icdf. Points must
            be non-negative and increasing.

        Returns
        -------
        NDArray[np.floating]
            The expected icdf values.
        """
        self._validate_params()
        if self.community_size_sequence is not None:
            return icdf(points, self.community_size_sequence)
        values = np.arange(self.min_community_size, self._get_max_community_size() + 1)
        weights = values**-self.community_size_exponent
        return icdf(points, values, weights=weights)
