# abcd-graph
A python library for generating ABCD graphs.

![tests](https://github.com/AleksanderWWW/abcd-graph/actions/workflows/ci.yml/badge.svg)
![pre-commit](https://github.com/AleksanderWWW/abcd-graph/actions/workflows/pre-commit.yml/badge.svg)
[![Release](https://img.shields.io/github/v/release/AleksanderWWW/abcd-graph)](https://github.com/AleksanderWWW/abcd-graph/releases)
![GitHub License](https://img.shields.io/github/license/AleksanderWWW/abcd-graph)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/abcd-graph)
![GitHub repo size](https://img.shields.io/github/repo-size/AleksanderWWW/abcd-graph)


## Installation

### Using `pip`
```bash
pip install abcd-graph
```
Project available at [PyPI](https://pypi.org/project/abcd-graph/).

### From source
```bash
git clone https://github.com/AleksanderWWW/abcd-graph.git

# or - with ssh - git clone git@github.com:AleksanderWWW/abcd-graph.git
cd abcd-graph
pip install .
```

If you're using `uv` then run the following for lightning-fast installation:
```bash
uv pip install -r pyproject.toml .
````

### Optional dependencies
The project comes with a set of optional dependencies that can be installed using the following commands:

```bash
pip install abcd-graph[dependency-name]
```

or

```bash
uv add abcd-graph --extra dependency-name
```

where `dependency-name` is one of the following:

| Value        | Packages installed                                                                |
|--------------|-----------------------------------------------------------------------------------|
| `dev`        | `pytest`, `pre-commit`, `pytest-cov`                                              |
| `matplotlib` | `matplotlib`                                                                      |
| `networkx`   | `networkx`                                                                        |
| `igraph`     | `igraph`                                                                          |
| `scipy`      | `scipy`                                                                           |
| `all`        | `networkx`, `igraph`, `scipy`, `matplotlib`                                       |


## Usage

```python
from abcd_graph import ABCDGraph, ABCDParams

params = ABCDParams(vcount=1000)
graph = ABCDGraph(params, logger=True).build()
```

### Parameters

- `params`: An instance of `ABCDParams` class.
- `logger` A boolean to enable or disable logging to the console. Default is `False` - no logs are shown.
- `callbacks`: A list of instances of `Callback` class. Default is an empty list.

### Returns

The `ABCDGraph` object with the generated graph.

### Graph generation parameters - `ABCDParams`

The `ABCDParams` class is used to set the parameters for the graph generation.

Arguments:

| Name                      | Type            | Description                                                  | Default |
|---------------------------|-----------------|--------------------------------------------------------------|---------|
| `vcount`                  | `int`           | Number of vertices in the graph                              | 1000    |
| `gamma`                   | `float`         | Power-law parameter for degrees, between 2 and 3             | 2.5     |
| `min_degree`              | `int`           | Min degree                                                   | 5       |
| `max_degree`              | `float`         | Parameter for max degree, between 0 and 1                    | 0.5     |
| `beta`                    | `float`         | Power-law parameter for community sizes, between 1 and 2     | 1.5     |
| `min_community_size`      | `int`           | Min community size                                           | 20      |
| `max_community_size`      | `float`         | Parameter for max community size, between `max_degree` and 1 | 0.8     |
| `xi`                      | `float`         | Noise parameter, between 0 and 1                             | 0.25    |
| `num_outliers`            | `int`           | Number of outlier vertices in the resulting graph            | 0       |
| `degree_sequence`         | `Sequence[int]` | Custom degree sequence to use during graph building          | None    |
| `community_size_sequence` | `Sequence[int]` | Custom community size sequence to use during graph building  | None    |

Parameters are validated when the object is created. If any of the parameters are invalid, a `ValueError` will be raised.

**Notes**
- You cannot pass both `degree_sequence` and any of `gamma`, `min_degree` or `max_degree`.
- You cannot pass both `community_size_sequence` and any of `beta`, `min_community_size` or `max_community_size`.


### Communities and edges

The `ABCDGraph` object has two properties that can be used to access the communities and edges of the graph.

- `communities` - A list of `ABCDCommunity` objects.
- `edges` - A list of tuples representing the edges of the graph.

Example:

```python

from abcd_graph import ABCDGraph, ABCDParams

params = ABCDParams(vcount=1000)

graph = ABCDGraph(params, logger=True).build()

print(graph.communities)
print(graph.edges)
```

Communities have the following properties:
- vertices - A list of vertices in the community.
- average_degree - The average degree of the community.
- degree_sequence - The degree sequence of the community.
- empirical_xi - The empirical xi of the community.

### Exporting

Exporting the graph to different formats is done via the `exporter` property of the `Graph` object.

Possible formats are:

| Method                         | Description                                                                               | Additional packages | Installation command               |
|--------------------------------|-------------------------------------------------------------------------------------------|---------------------|------------------------------------|
| `to_networkx()`                | Export the graph to a `networkx.Graph` object.                                            | `networkx`          | `pip install abcd-graph[networkx]` |
| `to_igraph()`                  | Export the graph to an `igraph.Graph` object.                                             | `igraph`            | `pip install abcd-graph[igraph]`   |
| `to_adjacency_matrix()`        | Export the graph to a `numpy.ndarray` object representing the adjacency matrix.           |                     |                                    |
| `to_sparse_adjacency_matrix()` | Export the graph to a `scipy.sparse.csr_matrix` object representing the adjacency matrix. | `scipy`             | `pip install abcd-graph[scipy]`    |


Example:

```python
from abcd_graph import ABCDGraph, ABCDParams

params = ABCDParams(vcount=1000)
graph = ABCDGraph(params, logger=True).build()
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

from abcd_graph import ABCDGraph, ABCDParams

from abcd_graph.callbacks import StatsCollector, Visualizer, PropertyCollector

stats = StatsCollector()
vis = Visualizer()
props = PropertyCollector()
params = ABCDParams(vcount=1000)
g = ABCDGraph(params, logger=True, callbacks=[stats, vis, props]).build()

print(stats.statistics)

print(props.xi_matrix)

vis.draw_community_cdf()
```

## Docker

To build a docker image containing the library, run:

```bash
docker build -t abcd-graph .
```

To run the image, use:

```bash
docker run -it abcd-graph /bin/bash
```
This will give you a terminal inside a container with the library installed.

Available are also installation commands for the additional packages:

```bash
docker build -t abcd-test --build-arg INSTALL_TYPE=igraph .
```

Possible values for `INSTALL_TYPE` are `dev`, `matplotlib`,  `networkx`, `igraph`, `scipy` and `all`.

| Value        | Packages installed                                                                |
|--------------|-----------------------------------------------------------------------------------|
| `dev`        | `pytest`, `pre-commit`, `pytest-cov`                                              |
| `matplotlib` | `matplotlib`                                                                      |
| `networkx`   | `networkx`                                                                        |
| `igraph`     | `igraph`                                                                          |
| `scipy`      | `scipy`                                                                           |
| `all`        | `networkx`, `igraph`, `scipy`, `matplotlib`                                       |

> [!WARNING]
> If you choose an option not included in the table above, the build process will fail.


## Examples

The library comes with a set of examples that show how to use the library in different scenarios.
You can find them in the `examples` directory in the format of Jupyter Notebooks.
