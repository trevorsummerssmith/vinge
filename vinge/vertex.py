"""
Data container classes for the graph.
"""

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

class NodeType:
    Left = 1
    Right = 2

class Vertex:
    """
    Abstract class done the pythonic way.
    see: http://docs.python.org/library/abc.html
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def nodetype(self):
        """
        Must be overridden by subclasses. Must return either
        NodeType.Left, or NodeType.Rig
        """
        pass

    @abstractmethod
    def __repr__(self):
        pass

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

    def nodetype(self):
        return NodeType.Left

    def __repr__(self):
        return "%d: %s '%s' '%s' %s" % (self.line_number, self.line, self.thread_id, self.message, self.time)

    def __eq__(self, other):
        if type(other) is not LogLineVertex:
            return False
        return self.line == other.line

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

    def nodetype(self):
        return NodeType.Right

    def __repr__(self):
        return '<%s>' % self.id

    def __eq__(self, other):
        if type(other) is not UniqueIDVertex:
            return False
        return self.id == other.id

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

    def nodetype(self):
        return NodeType.Right

    def __repr__(self):
        return '<%s,%s>' % (self.word, self.time)

    def __eq__(self, other):
        if type(other) is not TagVertex:
            return False
        return (self.word == other.word and
                self.time == other.time)
