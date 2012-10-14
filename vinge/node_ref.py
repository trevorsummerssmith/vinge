import re

"""
User commands want to reference a node by various syntax. This module parses
that syntax and produces a datatype to represent that parse.
"""

class NodeRefType:
    CURRENT = 0
    NEIGHBOR = 1

class NodeRef(object):
    """
    Output of parse_node_ref. This is just a algebraic datatype:
    The parsed node reference with its type.

    Can be:
      - current
      - neighbor(int)

    Attributes:
      type (NodeRefType.constant)
      neighbor_index (int): If the type is NodeRefType.NEIGHBOR
    """

    def __init__(self, node_ref_type, **kwargs):
        """
        Args:
            node_ref_type(NodeRefType.constant)
            kwargs:
                - if NEIGHBOR, then kwargs['neighbor_index]
        """
        self.type = node_ref_type
        if node_ref_type == NodeRefType.NEIGHBOR:
            self.neighbor_index = kwargs['neighbor_index']

    def __cmp__(self, other):
        if not isinstance(other, NodeRef):
            return NotImplemented
        elif self.type != other.type:
            return -1
        elif self.type == NodeRefType.CURRENT:
            return 0
        elif self.type == NodeRefType.NEIGHBOR:
            return cmp(self.neighbor_index, other.neighbor_index)
        else:
            raise ValueError("Programmer error: this should never happen")

def parse_node_ref(string):
    """
    node-ref is:
      - 'current' or 'cur'
      or
      - current|cur '.' neighbors|nbrs '[' idx ']'
        where idx is an integer

    This only parses and ensure the syntax is valid.

    Args:
        string (str):

    Returns: vertex.Vertex
    """
    # Janky for now. hand parser hell.
    m = re.match('^cur(rent)?(\.((nbrs|neighbors)\[(\d+)\]))?$', string)
    # No match return
    if not m:
        return None
    # it's just cur or current
    if not m.group(3):
        return NodeRef(NodeRefType.CURRENT)
    else:
        idx = int(m.group(5))
        return NodeRef(NodeRefType.NEIGHBOR, neighbor_index=idx)
