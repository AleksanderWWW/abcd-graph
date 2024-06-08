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
graph = Graph(params).build()
```

### Parameters

- `params`: An instance of `ABCDParams` class.
- `n`: Number of nodes in the graph.
- `model` A callable to build graph edges from a degree sequence. Default is a built-in implementation of the configuration model.
- `logger` A boolean to enable or disable logging to the console. Default is `False` - no logs are shown.


### Exporting

The graph object can be exported to `networkx.Graph` object using the `to_networkx` method.

```python
from abcd_graph import Graph, ABCDParams

params = ABCDParams()
graph = Graph(params).build().to_networkx()
```

This requires the `networkx` library to be installed.
```bash
pip install abcd-graph[networkx]
```

Another option is an `igraph.Graph` object.

```python
from abcd_graph import Graph, ABCDParams

params = ABCDParams()
graph = Graph(params).build().to_igraph()
```

This requires the `igraph` library to be installed.
```bash
pip install abcd-graph[igraph]
```

Finally, the graph can be exported to a `numpy.ndarray` object that represents the `adjacency matrix`.

```python
from abcd_graph import Graph, ABCDParams

params = ABCDParams()
graph = Graph(params).build().adj_matrix
```

> [!IMPORTANT]
> If the `build()` method is not run before calling any of the export methods, a `RuntimeError` will be raised.

> [!NOTE]
> The `numpy` array is of type `numpy.bool_`. If the graph was not properly generated (loops or multi-edges),
> a `MalformedGraphError` will be raised.
