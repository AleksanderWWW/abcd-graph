# Copyright (c) 2024 Jordan Barrett & Aleksander Wojnarowicz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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


def test_abcd_params_default_init():
    ABCDParams()
    assert True
