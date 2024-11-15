import random

from abcd_graph.graph.core.abcd_objects.edge import Edge


def build_recycle_list(adj_matrix: dict["Edge", int]) -> list["Edge"]:
    return [edge for edge in adj_matrix.keys() if adj_matrix[edge] > 1 or edge.is_loop]


def choose_other_edge(adj_matrix: dict["Edge", int], edge: "Edge") -> "Edge":
    edges = list(adj_matrix.keys())
    other_edge = random.choice(edges)
    while other_edge == edge:
        other_edge = random.choice(edges)

    return other_edge


def rewire_edge(adj_matrix: dict["Edge", int], edge: "Edge", other_edge: "Edge") -> None:
    if edge not in adj_matrix:
        return
    adj_matrix[edge] -= 1

    if adj_matrix[edge] == 0:
        del adj_matrix[edge]

    adj_matrix[other_edge] -= 1
    if adj_matrix[other_edge] == 0:
        del adj_matrix[other_edge]

    new_edge = Edge(edge.v1, other_edge.v1)

    if new_edge in adj_matrix:
        adj_matrix[new_edge] += 1
    else:
        adj_matrix[new_edge] = 1

    new_edge = Edge(edge.v2, other_edge.v2)

    if new_edge in adj_matrix:
        adj_matrix[new_edge] += 1
    else:
        adj_matrix[new_edge] = 1
