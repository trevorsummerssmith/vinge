"""
All public methods in this module should take two arguments:

  ctx (context.Context)
  args (kct.argparse.Namespace)

Each public method should correspond to a user method on the repl
(see repl.py).
"""

from format import format_vertex
from vinge.format import shorten_color_str
from graph import EdgeType

from kct.argparse import Namespace
from kct.output import pp, error, indent, deindent
import sys

import heapq
from vinge.filter import *
from vinge.regex import MatrixFilterRegex, ConcatRegex

def _print_regexes_header(ctx):
    """
    Pretty prints the regexes
    """
    pp("Regexes: ")
    for name, filter in ctx.regexes.iteritems():
        pp("  %s %s" % (name, filter.regex))
    # TODO(trevor) wordwrap

def _print_location(ctx):
    """
    Prints the previous log line, current log line and next log line.
    The current log line has the tags and ids highlighted. Previous
    and next log lines are just printed.
    """
    graph = ctx.graph
    posn = ctx.posn
    nbrs = graph[posn]
    # Grab the previous guy
    previous_neighbor = None
    next_neighbor = None
    for nbr in nbrs:
        edge_type = graph[posn][nbr].get('edge_type', None)
        if edge_type == EdgeType.ADJACENT_PREV:
            previous_neighbor = nbr
        elif edge_type == EdgeType.ADJACENT_NEXT:
            next_neighbor = nbr
    if previous_neighbor:
        print previous_neighbor
    print format_vertex(posn)
    if next_neighbor:
        print next_neighbor

def _print_neighbors(ctx):
    nbrs = ctx.sorted_neighbors(ctx.posn)
    print '_' * 10
    for i, nbr in enumerate(nbrs):
        print "%d %s %s" % (i,
                            ctx.graph[ctx.posn][nbr]['weight'],
                            shorten_color_str(format_vertex(nbr), 80))
        _print_most_likely_paths(ctx, nbr)

def _make_matrix_filter(transition, transition_op, filter, node):
    """
    This has a bad name.
    Make a new filter whose regex is: node filter.regex
    That is, start with the node passed in, followed by the regex in filter.

    Args:
        transition (scipy.sparse.base.spmatrix) Adjacency matrix of graph
        transition_op (scipy.sparse.linalg.LinearOperator) LinOp of transition
        filter (filter.Filter)
        node (vertex.Vertex)

    Returns:
        filter.Filter
    """
    # np.zeros returns a numpy array
    state = np.zeros(filter.graph.number_of_nodes())
    state[node.idx()] = 1.0
    node_regex = MatrixFilterRegex(filter.graph.number_of_nodes(),
                                   state, filter.graph)
    regex = ConcatRegex(transition, transition_op, node_regex, filter.regex)
    return Filter(regex, filter.graph)

def _most_likely_endpoints(ctx, filter, node, num_choose=4):
    """
    Calculates the most likely endpoints for the given filter,
    beginning at node.

    Args:
        ctx (context.Context)
        filter (filter.Filter)
        node (vertex.Vertex) the node to start the paths
        num_choose (int) the number of endpoints to return

    Returns:
        list of (int, float) - the index of the node in the graph's nodes array
            the float is the probability of the endpoint.
    """
    this_filter = _make_matrix_filter(ctx.transition,
                                      ctx.transition_op, filter, node)
    values = this_filter.calculate_values()
    most_likely = heapq.nlargest(num_choose, enumerate(values),
                                 key=lambda p: p[1])
    # TODO(trevor) num_choose should be able to be 'None' in which case
    # this returns the entire sorted list
    return most_likely

def _print_most_likely_paths(ctx, node):
    """
    Calculates and prints the most likely endpoints for all regexes
    in the context provided.
    """
    indent()
    for name, regex in ctx.regexes.iteritems():
        most_likely = _most_likely_endpoints(ctx, regex, node)
        nodes = ctx.graph.nodes() # cache this lookup
        pp("%s"%name)
        indent()
        for (idx, val) in most_likely:
            endpoint = nodes[idx]
            # Skip current
            if endpoint == ctx.posn or endpoint == node:
                continue
            pp("%s [%e]" % (str(endpoint)[:80], val))
        deindent()
    deindent()

def go_by_neighbor_index(ctx, args):
    """
    See go_by_vertex

    Args:
        ctx (context.Context)
        args (kct.argparse.Namepsace)
        args.idx - Index into the array of neighbors for ctx.posn

    Returns: None
    """
    idx = args.idx
    neighbors = ctx.graph[ctx.posn]
    # Assume stable sort on neighbors
    vertex = sorted(neighbors)[idx]
    go_by_vertex(ctx, Namespace(vertex=vertex))

def go_by_vertex(ctx, args):
    """
    Sets the context's posn to args.vertex.
    Prints the new posn, and its neighbors.

    Args:
        ctx (context.Context)
        args (kct.argparse.Namepsace)
        args.vertex (vertex.Vertex) - sets ctx.posn to this

    Returns: None
    """
    ctx.posn = args.vertex
    _print_location(ctx)
    _print_regexes_header(ctx)
    _print_neighbors(ctx)

def quit(ctx, args):
    print "goodbye (^_^)"
    sys.exit(0)

#
# Regex
#
def regex_list(ctx, args):
    """
    Prints the current regexes.
    """
    for name, filter in ctx.regexes.iteritems():
        pp("  %s: %s" % (name, str(filter.regex)))

def regex_add(ctx, args):
    """
    Adds a regex to the context's list of regexes.

    Args:
        ctx (context.Context)
        args (kct.argparse.Namepsace)
        args.name (str) - used to refer to the regex
        args.regex-str (str) - the regex in string form. A valid argument to
            regex_parser.compile_regex

    Returns: None
    """
    from vinge.filter import Filter
    from vinge.regex_parser import compile_regex, RegexParseException
    from vinge.regex_ast_to_regex import ast_to_regex
    name = args.name
    # argparse gives us an array of strings as the regex-str. We want a string
    regex_str = ' '.join(getattr(args, 'regex-str'))
    try:
        regex_ast = compile_regex(regex_str)
        regex = ast_to_regex(ctx.graph, ctx.transition, ctx.transition_op, regex_ast)
        # Add to the context
        ctx.regexes[name] = Filter(regex, ctx.graph)
        pp('Successfully added regex')
    except RegexParseException, rpe:
        error("Error parsing regex '%s': %s"%(regex_str, rpe.message))
