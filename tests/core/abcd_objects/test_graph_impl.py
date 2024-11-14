from unittest.mock import MagicMock

from abcd_graph.core.abcd_objects.community import Community
from abcd_graph.core.abcd_objects.edge import Edge
from abcd_graph.core.abcd_objects.graph_impl import XiMatrixBuilder
from abcd_graph.core.constants import OUTLIER_COMMUNITY_ID


def test_xi_matrix():
    comm_1 = MagicMock(spec=Community)
    comm_1.vertices = [1, 2, 3]
    comm_1.community_id = 0
    comm_1.degree_sequence = {1: 3, 2: 3, 3: 2}

    comm_2 = MagicMock(spec=Community)
    comm_2.vertices = [4, 5, 6]
    comm_2.community_id = 1
    comm_2.degree_sequence = {4: 3, 5: 3, 6: 2}

    outlier_comm = MagicMock(spec=Community)
    outlier_comm.vertices = [7, 8, 9]
    outlier_comm.community_id = OUTLIER_COMMUNITY_ID
    outlier_comm.degree_sequence = {7: 1, 8: 2, 9: 1}

    xi_builder = XiMatrixBuilder(
        xi=0.5,
        communities=[comm_1, comm_2, outlier_comm],
        adj_matrix={
            Edge(1, 2): 1,
            Edge(2, 3): 1,
            Edge(3, 1): 1,
            Edge(4, 5): 1,
            Edge(5, 6): 1,
            Edge(6, 4): 1,
            Edge(7, 8): 1,
            Edge(1, 4): 1,
            Edge(5, 8): 1,
            Edge(2, 9): 1,
        },
        deg_b={1: 1, 2: 1, 3: 0, 4: 1, 5: 0, 6: 0, 7: 1, 8: 2, 9: 1},
    )

    xi_builder.build()
