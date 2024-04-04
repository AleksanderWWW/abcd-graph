import pytest

from abcd_graph.abcd_params import ABCDParams


def test_abcd_params_invalid_gamma():
    with pytest.raises(ValueError):
        ABCDParams(gamma=1.5, delta=1, zeta=0.5, beta=1.5, tau=0.5, xi=0.5, s=1)


def test_abcd_params_invalid_zeta():
    with pytest.raises(ValueError):
        ABCDParams(gamma=2.5, delta=1, zeta=1.5, beta=1.5, tau=0.5, xi=0.5, s=1)


def test_abcd_params_invalid_beta():
    with pytest.raises(ValueError):
        ABCDParams(gamma=2.5, delta=1, zeta=0.5, beta=0.5, tau=0.5, xi=0.5, s=1)


def test_abcd_params_invalid_tau():
    with pytest.raises(ValueError):
        ABCDParams(gamma=2.5, delta=1, zeta=0.5, beta=1.5, tau=1.5, xi=0.5, s=1)


def test_abcd_params_invalid_xi():
    with pytest.raises(ValueError):
        ABCDParams(gamma=2.5, delta=1, zeta=0.5, beta=1.5, tau=0.5, xi=1.5, s=1)


def test_abcd_params_proper_init():
    ABCDParams(gamma=2.5, delta=1, zeta=0.5, beta=1.5, tau=0.5, xi=0.5, s=1)
    assert True
