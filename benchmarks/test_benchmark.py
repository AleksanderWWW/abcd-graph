import pytest

from abcd_graph import ABCD


@pytest.mark.benchmark
@pytest.mark.parametrize("n", [1000, 10000])
@pytest.mark.parametrize("xi", [0.2, 0.5, 0.7])
def test_benchmark_abcd(benchmark, n, xi):
    abcd = ABCD(n, xi=xi)
    benchmark(abcd.sample)


@pytest.mark.benchmark
@pytest.mark.parametrize("n", [1000, 10000])
@pytest.mark.parametrize("xi", [0.2, 0.5, 0.7])
@pytest.mark.parametrize("eta", [1.5, 2.0])
@pytest.mark.parametrize("rho", [0.0, -0.3, 0.3])
def test_benchmark_abcdoo(benchmark, n, xi, eta, rho):
    abcd = ABCD(n, xi=xi, eta=eta, rho=rho)
    benchmark(abcd.sample)
