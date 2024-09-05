# abcd-graph
A python library for generating ABCD graphs.

## Installation
```bash
pip install abcd-graph
```

## Usage
```python
from abcd_graph import Graph, ABCDParams

params = ABCDParams()
graph = Graph(params, n=1000, logger=True).build()
```

### Parameters

- `params`: An instance of `ABCDParams` class.
- `n`: Number of nodes in the graph.
- `logger` A boolean to enable or disable logging to the console. Default is `False` - no logs are shown.
- `callbacks`: A list of instances of `Callback` class. Default is an empty list.

### Returns

The `Graph` object with the generated graph.

### Graph generation parameters - `ABCDParams`

The `ABCDParams` class is used to set the parameters for the graph generation.

Arguments:

| Name    | Type    | Description                                              | Default |
|---------|---------|----------------------------------------------------------|---------|
| `gamma` | `float` | Power-law parameter for degrees, between 2 and 3         | 2.5     |
| `delta` | `int`   | Min degree                                               | 5       |
| `zeta`  | `float` | Parameter for max degree, between 0 and 1                | 0.5     |
| `beta`  | `float` | Power-law parameter for community sizes, between 1 and 2 | 1.5     |
| `s`     | `int`   | Min community size                                       | 20      |
| `tau`   | `float` | Parameter for max community size, between zeta and 1     | 0.8     |
| `xi`    | `float` | Noise parameter, between 0 and 1                         | 0.25    |

Parameters are validated when the object is created. If any of the parameters are invalid, a `ValueError` will be raised.

### Exporting

Exporting the graph to different formats is done via the `exporter` property of the `Graph` object.

Possible formats are:

| Method                         | Description                                                                               | Required packages | Installation command         |
|--------------------------------|-------------------------------------------------------------------------------------------|-------------------|------------------------------|
| `to_networkx()`                | Export the graph to a `networkx.Graph` object.                                            | `networkx`        | `pip install abcd[networkx]` |
| `to_igraph()`                  | Export the graph to an `igraph.Graph` object.                                             | `igraph`          | `pip install abcd[igraph]`   |
| `adj_matrix`                   | Export the graph to a `numpy.ndarray` object representing the adjacency matrix.           |                   |                              |
| `to_sparse_adjacency_matrix()` | Export the graph to a `scipy.sparse.csr_matrix` object representing the adjacency matrix. | `scipy`           | `pip install abcd[scipy]`    |
| `to_edge_list()`               | Export the graph to a list of tuples representing the edges.                              |                   |                              |


Example:
```python
from abcd_graph import Graph, ABCDParams

params = ABCDParams()
graph = Graph(params, n=1000, logger=True).build()
graph_networkx = graph.exporter.to_networkx()
```


### Callbacks

Callbacks are used to handle diagnostics and visualization of the graph generation process. They are instances of the `ABCDCallback` class.

Out of the box, the library provides three callbacks:
- `StatsCollector` - Collects statistics about the graph generation process.
- `PropertyCollector` - Collects properties of the graph.
- `Visualizer` - Visualizes the graph generation process.

Example:
```python

from abcd_graph import Graph, ABCDParams

from abcd_graph.callbacks import StatsCollector, Visualizer, PropertyCollector


stats = StatsCollector()
vis = Visualizer()
props = PropertyCollector()
params = ABCDParams()
g = Graph(params, n=1000, logger=True, callbacks=[stats, vis, props]).build()

print(stats.statistics)

print(props.xi_matrix)

vis.draw_community_cdf()
```
