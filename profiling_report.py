import cProfile
import pstats

from abcd_graph import (
    ABCDGraph,
    ABCDParams,
)

params = ABCDParams(vcount=1_000_000, num_outliers=1000)
g = ABCDGraph(params, logger=True)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    g.build()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")

    print()
    print("######## Profiling report (top 10% of cumulative time) ########")
    stats.print_stats(0.1)
