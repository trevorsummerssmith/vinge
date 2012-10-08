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
