from networkx import to_scipy_sparse_matrix
from scipy.sparse.linalg import aslinearoperator

from node_ref import NodeRefType

class ActiveSemex(object):
    """
    Simple wrapper around a semex that includes an active boolean.
    This is just a named tuple.

    Attributes:
        semex (semex.semex.Semex)
        active (bool)
    """
    def __init__(self, semex, active=True):
        self.semex = semex
        self.active = active

class Context(object):
    """
    Simple wrapper to define the state the program is working with.

    Attributes:
        graph (networkx.DiGraph)
        posn (vertext.Vertex) the current focus of the graph
        _semexes (dict str -> ActiveSemex):
            maps name of semex to the ActiveSemex. The ActiveSemex's
            active attribute is used by the context to keep track of semex
            state.
    """

    def __init__(self, graph, posn=None):
        """
        Args:
            graph (networkx.DiGraph)
            posn (vertex.Vertex) node currently 'focused' on
        """
        self.graph = graph
        self._graph_number_of_nodes = graph.number_of_nodes()
        self.posn = posn
        self._semexes = {}

        # Compute adjacency matrix and linear operator of adjacency matrix
        # For graph. We need this for our semexes.
        # TODO(trevor) this should be somewhere else. Here be some leaky abstracitions.
        self.transition = to_scipy_sparse_matrix(self.graph)
        self.transition_op = aslinearoperator(self.transition)

    def graph_number_of_nodes(self):
        # This is just here to cache this lookup. Probably should go elsewhere?
        return self._graph_number_of_nodes

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

    def semexes(self):
        """
        Returns:
            list of ActiveSemex
        """
        return self._semexes

    def add_semex(self, name, semex, active=True):
        self._semexes[name] = ActiveSemex(semex, active)

    def remove_semex(self, name):
        del self._semexes[name]

    def semex_toggle_active(self, name):
        old = self._semexes[name].active
        self._semexes[name].active = not old
        return old

    def semex_set_active(self, name, active):
        self._semexes[name].active = active

    def node_by_node_ref(self, node_ref):
        """
        Converts a context and a node_ref to a node.

        Args:
            node_ref (node_ref.NodeRef)

        Returns:
            vertex.Vertex

        Raises:
            ValueError if the node_ref is not valid in ctx
        """
        if node_ref.type == NodeRefType.CURRENT:
            node = self.posn
        elif node_ref.type == NodeRefType.NEIGHBOR:
            num_neighbors = len(self.graph[self.posn])
            idx = node_ref.neighbor_index
            if idx >= num_neighbors:
                msg = "Neighbor index out of bounds: "\
                    "got %d, but only %d neighbors"
                msg = msg % (idx, num_neighbors)
                raise ValueError(msg)
            node = self.sorted_neighbors(self.posn)[idx]
        return node
