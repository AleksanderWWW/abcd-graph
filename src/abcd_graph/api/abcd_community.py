from abcd_graph.core.typing import DegreeSequence


class ABCDCommunity:
    def __init__(
        self,
        community_id: int,
        vertices: list[int],
        average_degree: float,
        degree_sequence: DegreeSequence,
        empirical_xi: float,
    ) -> None:
        self._community_id = community_id
        self.vertices = vertices
        self.average_degree = average_degree
        self.degree_sequence = degree_sequence
        self.empirical_xi = empirical_xi

    def __repr__(self) -> str:
        return f"ABCDCommunityObj(id={self._community_id}, vertices={self.vertices[0]}-{self.vertices[-1]})"
