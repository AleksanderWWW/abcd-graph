import pytest

from abcd_graph import ABCDParams


@pytest.fixture(scope="session")
def params() -> ABCDParams:
    return ABCDParams()
