
import networkx as nx
import numpy as np
from vertex import UniqueIDVertex, TagVertex

def normalize_graph(g):
    '''For each vertex, normalize the weights of its out-edges so they
    sum to 1.0. (Unless they sum to 0.0, in which case leave them
    alone.) We assume that weights are non-negative.'''
    for u in g.nodes_iter():
        totwt = 0.0
        for (_,_,edata) in g.edges_iter(u, data=True):
            totwt += edata['weight']

        if totwt > 0.0:
            itotwt = 1.0 / totwt

            for (_,v) in g.edges_iter(u):
                g[u][v]['weight'] = itotwt * g[u][v]['weight'] 

class EdgeType:
    ADJACENT_PREV = 0,
    ADJACENT_NEXT = 1,
    DATA_TO_META = 2,
    META_TO_DATA = 3,
    META_TO_META = 4

def make_graph(loglines, tag_map, id_map, time_weighting, adjacent_logline_edge_weight=1.0, logline_id_edge_weight=1.0, logline_tag_edge_weight=1.0):

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
                
    normalize_graph(g)
        
    g = nx.freeze(g)
    return g
