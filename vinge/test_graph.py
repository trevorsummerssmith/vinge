import sys
import numpy as np 

from parser import parse_log_file
from graph import make_graph

def time_weighting(t1,t2):
#    return np.exp(-abs(t2-t1))
    return 1.0

def main():
    (log_line_vertices, tag_map, id_map) = parse_log_file(sys.argv[1])

    log_line_number = int(sys.argv[2])

    graph = make_graph(log_line_vertices, tag_map, id_map, time_weighting)
    posn = log_line_vertices[log_line_number]

    while True:
        print str(posn)[:30]
        print '_' * 10
        nbrs = graph.edges(posn)
        for i, nbr in enumerate(nbrs):
            print i, graph[posn][nbr]['weight'], nbr
#            print i, str(nbr)[:30]
        i = int(input('Go where?'))
        posn = nbrs[i]

if __name__ == '__main__':
    main()
