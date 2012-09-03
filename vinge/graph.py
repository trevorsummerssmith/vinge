
import networkx as nx
import numpy as np
from vertex import UniqueIDVertex, TagVertex

def make_graph(loglines, tag_map, id_map, time_weighting, max_tag_degree=10):

    g = nx.DiGraph()
    g.add_nodes_from(loglines)

    for id in id_map:
        v = UniqueIDVertex(id)
        g.add_node(v)
        for ll in id_map[id]:
            g.add_edge(ll, v, weight=1.0)
            g.add_edge(v, ll, weight=1.0)


    for tag in tag_map:
        # first, split up log lines by thread id
        thread_map = {}
        for ll in tag_map[tag]:
            if ll.thread_id not in thread_map:
                thread_map[ll.thread_id] = []
            thread_map[ll.thread_id].append(ll)

        for thread_id in thread_map:
            v, oldv = None, None
            num_ll_neighbors = 0

            for ll in thread_map[thread_id]:
                # make a newer version of the tag vertex whenever
                # degree is too high
                if v is None or num_ll_neighbors >= max_tag_degree:
                    oldv = v
                    v = TagVertex(tag, thread_id, ll.time)
                    g.add_node(v)
                    num_ll_neighbors = 0

                    # add edges between adjacent tag vertices, with
                    # weight based on how far apart the times are
                    if oldv is not None:
                        wt = time_weighting(v.time, oldv.time)
                        g.add_edge(v, oldv, weight=wt)
                        g.add_edge(oldv, v, weight=wt)

                g.add_edge(ll, v, weight=1.0)
                g.add_edge(v, ll, weight=1.0)
                num_ll_neighbors += 1
                
    # normalize weights so they sum to 1.0
    for u in g.nodes_iter():
        totwt = 0.0
        for (_,v,edata) in g.edges_iter(u, data=True):
            totwt += edata['weight']

        if totwt > 0.0:
            itotwt = 1.0 / totwt
        else:
            itotwt = 1.0

#        assert(totwt > 0.0)

        for (_,v) in g.edges_iter(u):
            g[u][v]['weight'] = itotwt * g[u][v]['weight'] 
        
    g = nx.freeze(g)
    return g
