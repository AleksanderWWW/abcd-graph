import random
import numpy as np


def rand_round(x):
    p = x - np.floor(x)
    if random.uniform(0, 1) <= p:
        return int(np.floor(x) + 1)
    else:
        return int(np.floor(x))


def powerlaw_distribution(choices: list[int], intensity: float) -> list[float]:
    norm = sum(y ** (-intensity) for y in choices)
    return [(y ** (-intensity)) / norm for y in choices]
