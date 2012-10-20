"""
Commands for interacting with regexes.
"""

from heapq import nlargest
from semex import ConcatRegex, MatrixFilterRegex

import numpy as np

def make_regex_starting_here(transition,
                             transition_op,
                             graph,
                             num_nodes,
                             regex,
                             node):
    """
    Make a new regex: node regex
    That is, start with the node passed in, followed by the regex.

    Args:
        transition (scipy.sparse.base.spmatrix) Adjacency matrix of graph
        transition_op (scipy.sparse.linalg.LinearOperator) LinOp of transition
        graph (networkx.DiGraph)
        num_nodes (int)
        regex (semex.semex.Regex)
        node (vertex.Vertex)

    Returns:
        semex.semex.Regex
    """
    state = np.zeros(num_nodes)
    state[node.idx()] = 1.0
    node_regex = MatrixFilterRegex(num_nodes, state, graph)
    new_regex = ConcatRegex(transition, transition_op, node_regex, regex)
    return new_regex

def most_likely_endpoints(regex, length, num_choose=4):
    """
    Calculates the most likely endpoints for the given regex.
    This assumes a uniform starting distribution.

    Args:
        regex (semex.semex.Regex)
        length (int)
        num_choose (int) the number of endpoints to return

    Returns:
        list of (int, float) - the index of the node in the graph's nodes array
            the float is the probability of the endpoint.
    """
    values = regex.linop_calculate_values(length)
    most_likely = nlargest(num_choose, enumerate(values),
                           key=lambda p: p[1])
    # TODO(trevor) num_choose should be able to be 'None' in which case
    # this returns the entire sorted list
    return most_likely
