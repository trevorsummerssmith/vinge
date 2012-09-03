
import networkx as nx
import numpy as np
from vertex import UniqueIDVertex, TagVertex

def make_graph(loglines, tag_map, id_map, time_weighting, adjacent_logline_edge_weight=1.0, logline_id_edge_weight=1.0, logline_tag_edge_weight=1.0):

    g = nx.DiGraph()
    g.add_nodes_from(loglines)

    oldll = None
    for ll in loglines:
        if oldll is not None:
            g.add_edge(oldll, ll, weight=adjacent_logline_edge_weight)
            g.add_edge(ll, oldll, weight=adjacent_logline_edge_weight)
        oldll = ll

    for id in id_map:
        v = UniqueIDVertex(id)
        g.add_node(v)
        for ll in id_map[id]:
            g.add_edge(ll, v, weight=logline_id_edge_weight)
            g.add_edge(v, ll, weight=logline_id_edge_weight)


    for tag in tag_map:
        v, oldv = None, None

        for ll in tag_map[tag]:
            oldv = v
            v = TagVertex(tag, ll.time)
            g.add_node(v)

            # add edges between adjacent tag vertices, with
            # weight based on how far apart the times are
            if oldv is not None:
                wt = time_weighting(v.time, oldv.time)
                g.add_edge(v, oldv, weight=wt)
                g.add_edge(oldv, v, weight=wt)

            g.add_edge(ll, v, weight=logline_tag_edge_weight)
            g.add_edge(v, ll, weight=logline_tag_edge_weight)
                
    # normalize weights so they sum to 1.0
    for u in g.nodes_iter():
        totwt = 0.0
        for (_,v,edata) in g.edges_iter(u, data=True):
            totwt += edata['weight']

#        assert(totwt > 0.0)

        if totwt > 0.0:
            itotwt = 1.0 / totwt

            for (_,v) in g.edges_iter(u):
                g[u][v]['weight'] = itotwt * g[u][v]['weight'] 
        
    g = nx.freeze(g)
    return g
