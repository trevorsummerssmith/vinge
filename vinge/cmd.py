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
import sys

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
    _print_neighbors(ctx)

def zoom_out(ctx):
    ctx.zoomlevel += 1
    _print_location(ctx)
    _print_neighbors(ctx)

def zoom_out(ctx):
    ctx.zoomlevel += 1
    _print_location(ctx)
    _print_neighbors(ctx)

def quit(ctx, args):
    print "goodbye (^_^)"
    sys.exit(0)
