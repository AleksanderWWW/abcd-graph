import pytest

from abcd_graph import (
    ABCDGraph,
    ABCDParams,
)


@pytest.fixture(scope="session")
def params() -> ABCDParams:
    return ABCDParams()


@pytest.fixture(scope="session")
def params_with_outliers() -> ABCDParams:
    return ABCDParams(num_outliers=100)


@pytest.fixture(scope="session")
def params_with_custom_sequences() -> ABCDParams:
    return ABCDParams(
        degree_sequence=[9] + [1] * 9,
        community_size_sequence=(5, 5),
        vcount=10,
    )


@pytest.fixture(scope="session")
def graph() -> ABCDGraph:
    return ABCDGraph()
