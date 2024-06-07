__all__ = ["rand_round", "powerlaw_distribution"]

import math
import random

import numpy as np
from numpy.typing import NDArray


def rand_round(x: float) -> int:
    p = x - math.floor(x)
    return int(math.floor(x) + 1) if random.uniform(0, 1) <= p else int(math.floor(x))


def powerlaw_distribution(choices: NDArray[np.int64], intensity: float) -> NDArray[np.float64]:
    dist: NDArray[np.float64] = (choices ** (-intensity)) / np.sum(choices ** (-intensity))
    return dist
