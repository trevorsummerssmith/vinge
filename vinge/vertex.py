"""
Data container classes for the graph.
"""

class NodeType:
    Left = 1
    Right = 2

class NodeKind:
    """
    Enum used to determine the type of the node.

    N.b. originally we were using isinstance checks in the code
    to determine the type of an instance. That turned out to be an insanely
    costly. This is cheap.
    """
    NodeKindLogLineVertex = 0
    NodeKindUniqueIDVertex = 1
    NodeKindTagVertex = 2
    NodeKindClusterVertex = 3

class Vertex(object):
    """
    Abstract class for Vertices
    """

    def nodetype(self):
        """
        Must be overridden by subclasses. Must return either
        NodeType.Left, or NodeType.Rig
        """
        raise NotImplemented

    def __repr__(self):
        raise NotImplemented

    def summarize(self):
        """
        Must be overridden by subclasses. Should return a dict of
        values that will be used in constructing labels for zoomed-out
        versions of the graph. It is OK to return an empty dict.
        """
        raise NotImplemented

class LogLineVertex(Vertex):
    """
    Vertex used to represent the log line itself.
    """
    def __init__(self, line, message, line_number, thread_id, time):
        """
        Args:
            line (str) Untouched log line from the original file
            message (str) message portion of the file
            line_number (int) 0 based index in original file
            thread_id (str) If relevant, thread identifier
            time (datetime.datetime)
        """
        # TODO(trevor) should these be optional?
        self.line = line
        self.message = message
        self.line_number = line_number
        self.thread_id = thread_id
        self.time = time
        self.kind = NodeKind.NodeKindLogLineVertex

    def nodetype(self):
        return NodeType.Left

    def __repr__(self):
        return "%d: %s '%s' '%s' %s" % (self.line_number, self.line, self.thread_id, self.message, self.time)

    def __eq__(self, other):
        if not isinstance(other, LogLineVertex):
            return NotImplemented
        return self.line == other.line

    def __lt__(self, other):
        if not isinstance(other, LogLineVertex):
            return NotImplemented
        return self.line < other.line

class UniqueIDVertex(Vertex):
    """
    Vertex used to represent an identifer. For example a search keyword.
    """
    def __init__(self, id):
        """
        Args:
            id (str)
        """
        self.id = id
        self.kind = NodeKind.NodeKindUniqueIDVertex

    def nodetype(self):
        return NodeType.Right

    def __repr__(self):
        return '<%s>' % self.id

    def __eq__(self, other):
        if not isinstance(other, UniqueIDVertex):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other):
        if not isinstance(other, UniqueIDVertex):
            return NotImplemented
        return self.id < other.id

class TagVertex(Vertex):
    """
    Vertex used to represent a word.
    """
    def __init__(self, word, time):
        """
        Args:
          word (str) the tag
          time (datetime.datetime)
        """
        self.word = word
        self.time = time
        self.kind = NodeKind.NodeKindTagVertex

    def nodetype(self):
        return NodeType.Right

    def __repr__(self):
        return '<%s,%s>' % (self.word, self.time)

    def __eq__(self, other):
        if not isinstance(other, TagVertex):
            return NotImplemented
        return (self.word, self.time) == (other.word, other.time)

    def __lt__(self, other):
        if not isinstance(other, TagVertex):
            return NotImplemented
        return  (self.word, self.time) < (other.word, other.time)
