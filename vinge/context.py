from networkx import to_scipy_sparse_matrix
from scipy.sparse.linalg import aslinearoperator

class ActiveRegex(object):
    """
    Simple wrapper around a regex that includes an active boolean.
    This is just a named tuple.

    Attributes:
        regex (semex.semex.Regex)
        active (bool)
    """
    def __init__(self, regex, active=True):
        self.regex = regex
        self.active = active

class Context(object):
    """
    Simple wrapper to define the state the program is working with.

    Attributes:
        graph (networkx.DiGraph)
        posn (vertext.Vertex) the current focus of the graph
        _regexes (dict str -> ActiveRegex):
            maps name of regex to the ActiveRegex. The ActiveRegex's
            active attribute is used by the context to keep track of regex
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
        self._regexes = {}

        # Compute adjacency matrix and linear operator of adjacency matrix
        # For graph. We need this for our regexes.
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

    def regexes(self):
        """
        Returns:
            list of ActiveRegex
        """
        return self._regexes

    def add_regex(self, name, regex, active=True):
        self._regexes[name] = ActiveRegex(regex, active)

    def remove_regex(self, name):
        del self._regexes[name]

    def regex_toggle_active(self, name):
        old = self._regexes[name].active
        self._regexes[name].active = not old
        return old

    def regex_set_active(self, name, active):
        self._regexes[name].active = active
