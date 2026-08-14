from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from abcd_graph.callbacks.abstract import ABCDCallback
from abcd_graph.graph import ABCDGraph
from abcd_graph.models import Model
from abcd_graph.params import ABCDParams

__all__ = ["ABCD"]


class ABCD:
    """Artificial Benchmark for Community Detection

    This class combines the ABCDGraph and ABCDParams class, essentially adding a
    sample method to ABCDParams.

    Parameters
    ----------

    vcount : int
        The number of vertices in the graph.

    gamma : float, default=2.5
        Powerlaw exponent for the degree distribution. Not used if
        degree_sequence is passed.

    beta: float, default=1.5
        Powerlaw exponent for the community size distribution. Not used if a
        custom community_size_sequence is passed.

    xi: float, default=0.25
        Proportion of edges in the global background graph. Setting xi=0 gives
        disjoint communities while xi=1 gives a random graph with no community
        structure.

    min_degree : int,  default=5
        Minimum degree in the graph. Not used if degree_sequence is passed.

    max_degree : int, default=30
        Maximum degree in the graph. Not used if degree_sequence is passed.

    min_community_size : int, default=20
        Minimum community size. Not used if a custom community_size_sequence
        is passed.

    max_community_size: int, default=250
        Maximum community size. Not used if a custom community_size_sequence
        is passed.

    degree_sequence : Sequence[int] | NDArray[np.int64] | None, default=None
        Used to pass a custom degree sequence that overrides the default
        powerlaw distribution.

    community_size_sequence : Sequence[int] | NDArray[np.int64] | None, default=None
        Used to pass a custom community size sequence that overrides the default
        powerlaw distribution. The sum of the community sizes must equal the number
        of vertices minus the number of outliers.

    num_outliers : int, default=0
        The number of outliers. These vertices have their entire degree in the
        global background graph so do not appear in any community.

    model : Model | None, default=None
        Random graph model used to sample the community and background graphs.

    verbose : bool, default=False
        Flag to log runtime infomation.
    """

    def __init__(
        self,
        vcount: int,
        gamma: float = 2.5,
        beta: float = 1.5,
        xi: float = 0.25,
        min_degree: int = 5,
        max_degree: int = 30,
        min_community_size: int = 20,
        max_community_size: int = 250,
        degree_sequence: Sequence[int] | NDArray[np.int64] | None = None,
        community_size_sequence: Sequence[int] | NDArray[np.int64] | None = None,
        num_outliers: int = 0,
        model: Model | None = None,
        verbose: bool = False,
    ):
        self.vcount = vcount
        self.xi = xi
        self.min_degree = min_degree
        self.max_degree = max_degree
        self.gamma = gamma
        self.min_community_size = min_community_size
        self.max_community_size = max_community_size
        self.beta = beta
        self.degree_sequence = degree_sequence
        self.community_size_sequence = community_size_sequence
        self.num_outliers = num_outliers
        self.model = model
        self.verbose = verbose

    def sample(self, callbacks: list[ABCDCallback] | None = None) -> ABCDGraph:
        """Sample an ABCD graph. Calling sample multiple times will overwrite
        the self.graph_ object."""
        self.params_ = ABCDParams(
            self.vcount,
            self.gamma if self.degree_sequence is None else None,
            self.beta if self.community_size_sequence is None else None,
            self.xi,
            self.min_degree if self.degree_sequence is None else None,
            self.max_degree if self.degree_sequence is None else None,
            self.min_community_size if self.community_size_sequence is None else None,
            self.max_community_size if self.community_size_sequence is None else None,
            self.degree_sequence,
            self.community_size_sequence,
            self.num_outliers,
        )

        self.graph_ = ABCDGraph(
            self.params_,
            logger=self.verbose,
            callbacks=callbacks,
        )

        self.graph_.build(self.model)

        return self.graph_
