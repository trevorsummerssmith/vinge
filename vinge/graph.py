
import networkx as nx
import numpy as np
from vertex import UniqueIDVertex, TagVertex

def normalize_graph(g):
    '''For each vertex, normalize the weights of its out-edges so they
    sum to 1.0. (Unless they sum to 0.0, in which case leave them
    alone.) We assume that weights are non-negative.'''
    # This function is called a lot and takes up a ton of time,
    # so I optimized it a bunch, comments below to aid readability.
    s = sum # cache global name lookup
    for u in g.nodes_iter():
        # Find the total weight of all edges for this node
        # Cache neighbors lookup, and use internal dict to avoid function call
        nbrs = g.succ[u]
        totwt = s([d['weight'] for d in nbrs.values()])

        if totwt > 0.0:
            itotwt = 1.0 / totwt
            nbrs = g.succ[u]
            for v in nbrs:
                nbrs[v]['weight'] *= itotwt

class EdgeType:
    """
    This is a bit janky -- the enum types here make restrictions on what nodes
    can use the different edges. Just be aware of this.
    """

    ADJACENT_PREV = 0,
    """
    LogLine to LogLine. Directional used to show the child node appeared
    previous to the parent in the original file.
    """

    ADJACENT_NEXT = 1,
    """
    LogLine to LogLine. Directional used to show the child node appeared post
    to the parent in the original file.
    """

    DATA_TO_META = 2,
    """
    LogLine to tag or id node.
    """

    META_TO_DATA = 3,
    """
    Tag or id node to LogLine.
    """

    META_TO_META = 4
    """
    Currently used for tag to tag.
    """

def make_graph(loglines,
               tag_map,
               id_map,
               time_weighting,
               adjacent_logline_edge_weight=1.0,
               logline_id_edge_weight=1.0,
               logline_tag_edge_weight=1.0):
    """
    Creates a digraph from the argument data.

    The graph that is created has the following structure:
      o LogLine nodes have one edge to their previous LogLine
        and one to its next Logline. This is defined by their position
        in the loglines array argument.
      o LogLine nodes have one DATA_TO_META edge to every id node, based upon
        the entry in the id_map argument.
      o LogLine nodes have one DATA_TO_META edge to each tag node.

      o Id nodes have one META_TO_DATA edge to each of their LogLine nodes.

      o Tag nodes have one META_TO_DATA edge to each of their LogLine nodes.
      o Tag nodes each have two META_TO_META edges -- one to the 'previous'
        tag node and one to the 'next' tag node. 'next' and 'previous' are
        defined by the TagVertex.time field.

      o The graph is directed, but every directed edge has a corresponding
        directed edge -- if an edge (u,v) exists then (v,u) (of some type)
        exists.

    TODO(trevor) once we're further along and we like this graph take a few
    minutes and make a asciigraph example.

    Args:
        loglines see vinge.parser.parse_log return value
        tag_map see vinge.parser.parse_log return value
        id_map see vinge.parser.parse_log return value
        time_weighting (fun (datetime.datetime, datetime.datetime) -> float)
            function defining the weight between tag nodes
        adjacent_logline_edge_weight (float)
        logline_id_edge_weight (float)
        logline_tag_edge_weight (float)

    Returns:
        networkx.DiGraph
    """

    g = nx.DiGraph()
    g.add_nodes_from(loglines)

    oldll = None
    for ll in loglines:
        if oldll is not None:
            g.add_edge(oldll, ll, weight=adjacent_logline_edge_weight,
                       edge_type=EdgeType.ADJACENT_NEXT)
            g.add_edge(ll, oldll, weight=adjacent_logline_edge_weight,
                       edge_type=EdgeType.ADJACENT_PREV)
        oldll = ll

    for id in id_map:
        v = UniqueIDVertex(id)
        g.add_node(v)
        for ll in id_map[id]:
            g.add_edge(ll, v, weight=logline_id_edge_weight,
                       edge_type=EdgeType.DATA_TO_META)
            g.add_edge(v, ll, weight=logline_id_edge_weight,
                       edge_type=EdgeType.META_TO_DATA)


    for tag in tag_map:
        v, oldv = None, None

        the_tag_occurrences = sorted(list(tag_map[tag]))
        for ll in the_tag_occurrences:
            oldv = v
            v = TagVertex(tag, ll.time)
            g.add_node(v)

            # add edges between adjacent tag vertices, with
            # weight based on how far apart the times are
            if oldv is not None:
                wt = time_weighting(v.time, oldv.time)
                g.add_edge(v, oldv, weight=wt, edge_type=EdgeType.META_TO_META)
                g.add_edge(oldv, v, weight=wt, edge_type=EdgeType.META_TO_META)

            g.add_edge(ll, v, weight=logline_tag_edge_weight,
                       edge_type=EdgeType.DATA_TO_META)
            g.add_edge(v, ll, weight=logline_tag_edge_weight,
                       edge_type=EdgeType.META_TO_DATA)
                
    # Normalize edge weights
    normalize_graph(g)

    # Add the vertex index to all nodes
    for i, node in enumerate(g.nodes_iter()):
        node._set_idx(i)
        
    g = nx.freeze(g)
    return g
