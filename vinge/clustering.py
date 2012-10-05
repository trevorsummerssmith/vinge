
import networkx as nx
import numpy as np
from vertex import UniqueIDVertex, TagVertex

def _threshold_nicely(v, old_labeling, lvl): 
    pass
# labeling, themap = _threshold_nicely(evecs[1], cluster_labels[-1], lvl)
# return new_labeling, themap

# init new labeling
# set next_cluster_label to 0

# iter over clusters in old_labeling
#   make a list of v values
#   sort the list
#   pick out median

#   write new labels for this cluster, checking that we are not
#   over-writing any valid labels

# check that everything got a labeling

def _make_graph_of_level(self.labelings[i]): 
    pass

# iter over clusters
#   iter over vertices
#     run vertex_summary_map on each vertex
#   run vertex_summary_reduce on the map outputs, get summary
#   make a node for the cluster, put the summary in its data

# make edges somehow??? 

# we want to retain sparsity when the graph is large, but maybe not
# once it gets sufficiently small? Let's say that we are given a
# maximum number of edges, and if the n(n-1) is less than that, make a
# dense graph. Otherwise, use the obvious graph induced by the
# hierarchical clustering.


#return gf

def _delete_inter_cluster_links(graph, labeling): 
    edges_to_delete = []

    for (u,v) in graph.edges_iter():
        if labeling[u.id] != labeling[v.id]:
            edges_to_delete.append( (u,v) )

    for (u,v) in edges_to_delete:
        graph.remove_edge(u,v)
        

class Clustering(object):
    """
    Represents a hierarchical clustering of graph nodes, that we can
    use to zoom in and out.

    Each level of the hierarchy is represented as a numpy array of
    integer values. These give a cluster label for each node; the
    labels of the clusters are arbitrary.

    clust.map is a list of maps between the levels, which is
    represented as a list of dicts. clust.map specifies a tree that
    represents the hierarchical decomposition. If clust.map[i][j] = k,
    then the cluster #j in level i contains the cluster #k in
    level i+1.
    """

    def __init__(self, graph, num_lvls, cluster_labels, cluster_maps, vertex_summary_map, vertex_summary_reduce)
        self.num_lvls = num_lvls
        self.labelings = cluster_labelings
        self.maps = cluster_maps

        self.graphs = [graph]
        for i in xrange(1, num_lvls+1):
            gf = _make_graph_of_level(self.labelings[i])            
            gf.freeze()
            self.graphs.append(gf)

def cluster_graph(graph, num_lvls, vertex_summary_map, vertex_summary_reduce):
    dirty_graph = graph.copy()
    dirty_graph.unfreeze()
    coarsest_labeling = np.ones(dirty_graph.num_nodes())
    cluster_labels = [coarsest_labeling]
    cluster_maps = []

    for lvl in xrange(1, num_lvls+1):
        # find the second left eigenvector, it gives us a clustering
        # (NB: left eigenvectors are right eigenvectors of the
        # transpose)
        smat = dirty_graph.to_scipy_sparse_matrix()
        tsmat = smat.transpose()
        print type(smat), type(tsmat)
        evals, evecs = scipy.sparse.linalg.eigs(tsmat, k=2)
        print lvl, evals
        
        labeling, themap = _threshold_nicely(evecs[1], cluster_labels[-1], lvl)
        _delete_inter_cluster_links(dirty_graph, labeling)

        cluster_labels.append(labeling)
        cluster_maps.append(themap)
        
    return Clustering(graph, num_lvls, cluster_labels, cluster_maps, vertex_summary_map, vertex_summary_reduce)
    
