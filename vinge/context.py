from networkx import to_scipy_sparse_matrix
from scipy.sparse.linalg import aslinearoperator

class Context(object):
    """
    Simple wrapper to define the state the program is working with.
    """

    def __init__(self, graph, posn=None):
        """
        Args:
            graph (networkx.DiGraph)
            posn (vertex.Vertex) node currently 'focused' on
        """
        self.graph = graph
        self.posn = posn
        self.regexes = {}

        # Compute adjacency matrix and linear operator of adjacency matrix
        # For graph. We need this for our regexes.
        # TODO(trevor) this should be somewhere else. Here be some leaky abstracitions.
        self.transition = to_scipy_sparse_matrix(self.graph)
        self.transition_op = aslinearoperator(self.transition)

    def sorted_neighbors(self, node):
        """
        Returns the neighbors of node. Sorted in a way that will remain stable
        between calls. The purpose of this is so that views can print indices of
        the neighbor nodes and have that be meaningful.

        Args:
            node (vertex.Vertex): the node whose neighbors to return

        Returns:
            list of vertex.Vertex
        """
        return sorted(self.graph[node])
