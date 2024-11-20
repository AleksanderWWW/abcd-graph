import time

import tabulate

from abcd_graph import (
    ABCDGraph,
    ABCDParams,
)

START = 100_000
STOP = 1_000_000
STEP = 100_000


def main() -> None:
    stats = []
    for i, vcount in enumerate(range(START, STOP + STEP, STEP)):
        y = time_build(vcount)

        if vcount == START:
            delta_y = 0
        else:
            delta_y = y - stats[int(i) - 1][1]

        stats.append((vcount, y, delta_y))

    table = tabulate.tabulate(stats, headers=["Vertices", "Time (s)", "Delta time (s)"])
    print(table)


def time_build(vcount) -> float:
    params = ABCDParams(vcount=vcount)
    g = ABCDGraph(params, logger=False)
    start = time.perf_counter()
    g.build()
    return time.perf_counter() - start


if __name__ == "__main__":
    main()
