import pytest

from abcd_graph import ABCDParams


@pytest.fixture(scope="session")
def params() -> ABCDParams:
    return ABCDParams()


@pytest.fixture(scope="session")
def params_with_outliers() -> ABCDParams:
    return ABCDParams(num_outliers=100)
