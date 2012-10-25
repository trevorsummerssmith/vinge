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
from kct.output import pp, error, indent, info, deindent
import kct.color as color
import sys

import heapq
from vinge.filter import *
from vinge.node_ref import parse_node_ref, NodeRef, NodeRefType
from vinge.semex.semex import MatrixSensorSemex, ConcatSemex
from semex.porcelain import make_regex_starting_here, most_likely_endpoints

def _print_regexes_header(ctx):
    """
    Pretty prints the regexes
    """
    pp("Regexes: ")
    for name, regex in ctx.regexes().iteritems():
        pp("  %s %s" % (name, regex.regex))
    # TODO(trevor) wordwrap

def _print_location(ctx, cur_node=None):
    """
    Prints the previous log line, current log line and next log line.
    The current log line has the tags and ids highlighted. Previous
    and next log lines are just printed.
    """
    graph = ctx.graph
    if not cur_node:
        node = ctx.posn
    else:
        node = cur_node
    nbrs = graph[node]
    # Grab the previous guy
    previous_neighbor = None
    next_neighbor = None
    for nbr in nbrs:
        edge_type = graph[node][nbr].get('edge_type', None)
        if edge_type == EdgeType.ADJACENT_PREV:
            previous_neighbor = nbr
        elif edge_type == EdgeType.ADJACENT_NEXT:
            next_neighbor = nbr
    if previous_neighbor:
        print previous_neighbor
    print format_vertex(node)
    if next_neighbor:
        print next_neighbor

def _print_neighbors(ctx, cur_node=None):
    if cur_node is None:
        node = ctx.posn
    else:
        node = cur_node
    nbrs = ctx.sorted_neighbors(node)
    print '_' * 10
    for i, nbr in enumerate(nbrs):
        print "%d %s" % (i,
                         shorten_color_str(format_vertex(nbr), 80))
        _print_most_likely_paths(ctx, nbr)

def _print_most_likely_paths(ctx, node):
    """
    Calculates and prints the most likely endpoints for all regexes
    in the context provided.
    """
    indent()
    graph = ctx.graph
    num_nodes = ctx.graph_number_of_nodes()
    for name, val in ctx.regexes().iteritems():
        if not val.active:
            continue
        # Calculate regex starting at this neighbor node
        regex = val.regex
        this_regex = make_regex_starting_here(ctx.transition,
                                              ctx.transition_op,
                                              graph,
                                              num_nodes,
                                              regex,
                                              node)
        most_likely = most_likely_endpoints(this_regex, num_nodes)
        nodes = graph.nodes() # cache this lookup
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
    vertex = ctx.sorted_neighbors(ctx.posn)[idx]
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

def node_info(ctx, args):
    """
    Args:
        ctx (context.Context)
        args (kct.argparse.Namespace)
        args.node-ref
    """
    node_ref_str = getattr(args, 'node-ref')
    # info command without anything is 'current'
    if node_ref_str is None:
        node_ref_str = 'cur'

    node_ref = parse_node_ref(node_ref_str)
    if node_ref is None:
        # TODO(trevor) print node-ref types in help msg
        error("Error %s is not a valid node-ref" % node_ref_str)
        return

    try:
        node = ctx.node_by_node_ref(node_ref)
        _print_location(ctx, node)
        _print_regexes_header(ctx)
        _print_neighbors(ctx, node)
    except ValueError, ve: # Catch invalid node-ref
        error(ve)
        return

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
    for name, regex in ctx.regexes().iteritems():
        pp("  %s: %s" % (name, str(regex.regex)))

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
    from vinge.semex.parser import compile_regex, RegexParseException
    from vinge.semex.ast_to_semex import ast_to_regex
    name = args.name
    # argparse gives us an array of strings as the regex-str. We want a string
    regex_str = ' '.join(getattr(args, 'regex-str'))
    try:
        regex_ast = compile_regex(regex_str)
        regex = ast_to_regex(ctx.graph, ctx.transition, ctx.transition_op, regex_ast)
        # Add to the context
        ctx.add_regex(name, regex)
        pp('Successfully added regex')
    except RegexParseException, rpe:
        error("Error parsing regex '%s': %s"%(regex_str, rpe.message))

_bool_to_active = {True:color.green('active'), False:color.red('inactive')}

def regex_toggle(ctx, args):
    """
    Swaps the active status of the provided regex. Active regexes are used in
    various display commands (see e.g. cmd.node_info).

    Args:
        ctx (context.Context)
        args (kct.argparse.Namepsace)
        args.name (str) - used to refer to the regex

    Returns: None
    """
    name = args.name
    try:
        is_active = not ctx.regex_toggle_active(name)
        info("%s is now %s" % (name, _bool_to_active[is_active]))
    except KeyError, ke:
        # TODO(trevor) catching keyerror here is bad. Probs masking something
        error("Unknown regex '%s'" % name)

def regex_peek(ctx, args):
    name = args.name
    node_ref_str = getattr(args, 'node-ref')
    node_ref = parse_node_ref(node_ref_str)
    if node_ref is None:
        error("Error %s is not a valid node-ref" % node_ref_str)
        return
    node = ctx.node_by_node_ref(node_ref)

    active_regex = ctx.regexes().get(name)
    if active_regex is None:
        error("Error unknown regex '%s'" % name)
    regex = active_regex.regex

    new_regex = make_regex_starting_here(ctx.transition, ctx.transition_op,
                                         ctx.graph, ctx.graph_number_of_nodes(),
                                         regex, node)
    most_likely = most_likely_endpoints(new_regex, ctx.graph_number_of_nodes())
    for (idx, val) in most_likely:
        endpoint = ctx.graph.nodes()[idx]
        pp("%s [%e]" % (str(endpoint)[:80], val))
