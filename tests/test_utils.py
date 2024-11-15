from unittest.mock import patch

import pytest

from abcd_graph.utils import (
    require,
    seed,
)


@patch("numpy.random.seed")
@patch("random.seed")
def test_seed(mock_random_seed, mock_numpy_seed):
    seed(42)

    mock_random_seed.assert_called_with(42)
    mock_numpy_seed.assert_called_with(42)


def test_require():
    @require("non-existent-package")
    def func():
        import non_existent_package  # noqa: F401

        return

    with pytest.raises(ImportError):
        func()
