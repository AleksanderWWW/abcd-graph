from typing import Any

import numpy as np
import scipy.sparse as sp
from numba import njit
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import minimize_scalar


@njit
def count_intra_community_edges(
    edges: NDArray[np.integer[Any]],
    indptr: NDArray[np.int32] | NDArray[np.int64],
    indices: NDArray[np.int32] | NDArray[np.int64],
):
    m_intra_community = 0
    for i in range(edges.shape[0]):
        u, v = edges[i]
        u_coms = indices[indptr[u] : indptr[u + 1]]
        v_coms = indices[indptr[v] : indptr[v + 1]]
        m_intra_community += int(np.any(np.isin(u_coms, v_coms)))
    return m_intra_community


def icdf(
    points: ArrayLike, sequence: ArrayLike, weights: ArrayLike | None = None
) -> NDArray[np.floating]:
    points = np.asarray(points)
    points = np.insert(points, 0, 0)
    hist, bin_edges = np.histogram(sequence, bins=points, weights=weights)  # type: ignore
    cdf = np.cumsum(hist).astype(np.float64)
    cdf /= cdf[-1]
    icdf = 1 - cdf
    return icdf


def fit_powerlaw_exponent(
    samples: NDArray[np.integer[Any]],
):
    """Find the parameters of a discrete truncated power-law
    distribution for the given samples via maximum-likelihood.
    Sets the bounds to the minimum and maximum observed samples
    and computes the optimal exponent.

    Parameters
    ----------
    samples: NDArray
        An array of samples to which we fit the parameters

    Returns
    -------
    exponent: float
        The fit exponent.

    x_min: int
        The lower bound on the fit distribution, will be the smallest
        value sampled.

    x_max: int
        The fit (or passed) upper bound on the fit distribution.
    """
    x_min = np.min(samples)
    x_max = np.max(samples)

    values, counts = np.unique_counts(samples)
    x_frequency = np.zeros(x_max - x_min + 1, dtype=np.float64)
    x_frequency[values - x_min] = counts

    domain = np.arange(x_min, x_max + 1, dtype=np.float64)
    log_domain = np.log(domain)

    observed_constant = np.sum(x_frequency * log_domain)

    # Log-likelihood equation for truncated power-law, negated
    # since scipy has a minimizer
    def objective(exponent):
        weights = domain ** (-exponent)
        return len(samples) * np.log(np.sum(weights)) + exponent * observed_constant

    sol = minimize_scalar(objective, bounds=[0.0, 5.0], method="Bounded")
    return sol.x


class ABCDSample:
    """A sample from the ABCD model.

    Consists of an edge list and a community-node membership matrix.
    Has functions for measuring empirical properties of the graph, and
    functions for converting the edge list to other common graph types.

    Parameters
    ----------
    edges: NDArray
        List of edges. If dtype is integers, assumed to be contiguous and
        treated as node ids. If dtype is anything else, they will be
        assigned contiguous integer ids.
    membership_matrix: sp.sparray | sp.spmatrix | ArrayLike
        Community x node sparse membership array, 2-d community x node dense
        membership array, or 1-d array of community ids.
    """

    def __init__(
        self,
        edges: ArrayLike,
        communities: sp.sparray | sp.spmatrix | ArrayLike,
    ):
        edges = np.asarray(edges)
        if not np.issubdtype(edges.dtype, np.integer):
            _, edges = np.unique(edges, return_inverse=True)
            edges = edges.astype(np.min_scalar_type(np.max(edges)))
        self.edges = edges

        if sp.issparse(communities):
            self.membership_matrix = sp.csr_array(communities, dtype=np.bool)
        else:
            communities = np.asarray(communities)
            if communities.ndim == 2:
                self.membership_matrix = sp.csr_array(communities, dtype=np.bool)
            elif communities.ndim == 1 and np.issubdtype(communities.dtype, np.integer):
                n = len(communities)
                node_ids = np.arange(n, dtype=communities.dtype)
                membership = np.vstack([communities, node_ids])
                membership = membership[:, membership[0] >= 0]  # Drop outliers
                membership_matrix = sp.coo_array(
                    (np.ones(membership.shape[1], dtype=np.bool), membership),
                    shape=(np.max(communities) + 1, n),
                )
                self.membership_matrix = membership_matrix.tocsr()
            else:
                raise ValueError(
                    """Got an unknown format for communities. Must be a sparse or dense
                    membership matrix or a 1-d array of community ids."""
                )

    @property
    def n(self) -> int:
        """The number of vertices in the graph.

        Returns
        -------
        int
        """
        return self.membership_matrix.shape[1]

    @property
    def m(self) -> int:
        """The number of edges in the graph.

        Returns
        -------
        int
        """
        return self.edges.shape[0]

    @property
    def xi(self) -> float:
        """The proportion of inter-community edges.

        Returns
        -------
        float
        """
        membership_csc = self.membership_matrix.tocsc()
        m_intra_community = count_intra_community_edges(
            self.edges,
            membership_csc.indptr,
            membership_csc.indices,
        )
        return 1 - (m_intra_community / self.m)

    @property
    def outliers(self) -> int:
        """The number of outlier vertices (belong to no community).

        Returns
        -------
        int
        """
        return np.sum(self.membership_matrix.count_nonzero(axis=0) == 0)

    @property
    def eta(self) -> float:
        """The average number of communities per non-outlier vertex.

        Returns
        -------
        float
        """
        return self.membership_matrix.sum() / (self.n - self.outliers)

    @property
    def rho(self) -> float:
        """The pearson correlation between the degree and number of communities
        to which they belong for non-outlier nodes.

        Returns
        -------
        float
        """
        if self.eta == 1:
            return 1.0
        degrees = self.degree_sequence
        coms_per_node = self.membership_matrix.sum(axis=0)
        inlier_mask = coms_per_node > 0
        rho = np.corrcoef(degrees[inlier_mask], coms_per_node[inlier_mask])[0, 1]
        return rho

    @property
    def degree_sequence(self) -> NDArray:
        """The degree sequence.

        Returns
        -------
        Array[int]
        """
        node, degree = np.unique_counts(self.edges)
        return degree[node]

    @property
    def min_degree(self) -> int:
        """The minimum degree.

        Returns
        -------
        int
        """
        return np.min(self.degree_sequence)

    @property
    def max_degree(self) -> int:
        """The maximum degree.

        Returns
        -------
        int
        """
        return np.max(self.degree_sequence)

    @property
    def degree_exponent(self) -> float:
        """The measured degree exponent

        Returns
        -------
        float
        """
        degree_sequence = self.degree_sequence
        exponent = fit_powerlaw_exponent(degree_sequence)
        return exponent

    @property
    def community_size_sequence(self) -> NDArray:
        """The community size sequence.

        Returns
        -------
        Array[int]
        """
        return self.membership_matrix.sum(axis=1)

    @property
    def min_community_size(self) -> int:
        """The minimum community size.

        Returns
        -------
        int
        """
        return np.min(self.community_size_sequence)

    @property
    def max_community_size(self) -> int:
        """The maximum community size.

        Returns
        -------
        int
        """
        return np.max(self.community_size_sequence)

    @property
    def community_size_exponent(self) -> float:
        """The measured community size exponent.

        Returns
        -------
        float
        """
        size_sequence = self.community_size_sequence
        exponent = fit_powerlaw_exponent(size_sequence)
        return exponent

    def to_sparse(self, matrix: bool = False) -> sp.csr_array | sp.csr_matrix:
        """Format the graph as a sparse adjacency matrix.

        Parameters
        ----------
        matrix: bool, default=False
            Flag to make the return type the deprecated scipy.sparse.csr_matrix.
            This is useful for passing to scikit-network algorithms as they currently
            do not accept the modern scipy.sparse.csr_array type.

        Returns
        -------
        sp.csr_array | sp.csr_matrix
        """
        adjacency = sp.coo_array(
            (np.ones(self.edges.shape[0], dtype=np.bool), self.edges.T),
            shape=(self.n, self.n),
        )
        adjacency = adjacency + adjacency.transpose()
        if matrix:
            adjacency = sp.coo_matrix(adjacency)
        return adjacency.tocsr()

    def to_dense(self) -> NDArray[np.bool]:
        """Format the graph as an adjacency matrix.

        Returns
        -------
        Array
        """
        return self.to_sparse().todense()

    def to_networkx(self):
        """Format the graph as a networkx object.

        Returns
        -------
        networkx.Graph
        """
        try:
            import networkx as nx  # type: ignore

            g = nx.from_edgelist(self.edges)
            return g
        except ImportError as e:
            raise ImportError(
                "Package 'networkx' is not installed. "
                "Run `pip install networkx` to install it."
            ) from e

    def to_igraph(self):
        """Format the graph as an igraph object.

        Returns
        -------
        igraph.Graph
        """
        try:
            import igraph as ig  # type: ignore

            g = ig.Graph(n=self.n, edges=self.edges, directed=False)
            return g
        except ImportError as e:
            raise ImportError(
                "Package 'igraph' is not installed. "
                "Run `pip install igraph` to install it."
            ) from e

    @property
    def community_array(self):
        """Format the community membership matrix as an array of community ids.
        The value at index i is the community id of vertex i. Following hdbscan
        convention, communities are indexed 0-n and -1 is used for outliers.

        Returns
        -------
        Array[int]
        """
        if self.eta > 1:
            raise ValueError(
                "Overlapping communities cannot be represented with an array"
            )
        result = np.full(self.n, -1)
        coms, nodes = self.membership_matrix.nonzero()
        result[nodes] = coms
        return result

    @property
    def community_dict(self):
        """Format the community membership matrix as a dictionary with community ids
        as keys and sets of nodes as values.

        Returns
        -------
        dict[int, set]
        """
        indptr = self.membership_matrix.indptr
        indices = self.membership_matrix.indices
        return {
            i: set(indices[indptr[i] : indptr[i + 1]]) for i in range(len(indptr) - 1)
        }

    def degree_icdf(self, points: ArrayLike):
        """Measure the inverse cumulative distribution function (icdf)
        of the degree distribution at a sequence of values

        Parameters
        ----------
        points: ArrayLike
            An array of points at which to mearuse the icdf.

        Returns
        -------
        NDArray[np.floating]
            The measured icdf values.
        """
        return icdf(points, self.degree_sequence)

    def community_size_icdf(self, points: ArrayLike):
        """Measure the inverse cumulative distribution function (icdf)
        at of the community size distribution a sequence of values

        Parameters
        ----------
        points: ArrayLike
            An array of points at which to mearuse the icdf.

        Returns
        -------
        NDArray[np.floating]
            The measured icdf values.
        """
        return icdf(points, self.community_size_sequence)
