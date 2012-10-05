class Context(object):
    """
    Simple wrapper to define the state the program is working with.
    """

    def __init__(self, graph, clustering, posn=None):
        """
        Args:
            graph (networkx.DiGraph)
            posn (vertex.Vertex) node currently 'focused' on
        """
        self.graph = graph
        self.posn = posn
        self.clustering = clustering
        self.zoomlevel = 0
