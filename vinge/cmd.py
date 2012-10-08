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
    nbrs = ctx.graph[ctx.posn]
    print '_' * 10
    for i, nbr in enumerate(sorted(nbrs)):
        print "%d %s %s" % (i,
                            ctx.graph[ctx.posn][nbr]['weight'],
                            shorten_color_str(format_vertex(nbr), 80))

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
