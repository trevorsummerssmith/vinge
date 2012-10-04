import numpy as np
from vinge.vertex import LogLineVertex, TagVertex, UniqueIDVertex, NodeKind

def is_tag(v):
    if v.kind == NodeKind.NodeKindTagVertex:
        return 1.0
    else:
        return 0.0

def is_line(v):
    if v.kind == NodeKind.NodeKindLogLineVertex:
        return 1.0
    else:
        return 0.0

def number_of_es(v):
    if v.kind == NodeKind.NodeKindLogLineVertex:
        return v.message.lower().count('e')
    elif v.kind == NodeKind.NodeKindUniqueIDVertex:
        return 0.0
    elif v.kind == NodeKind.NodeKindTagVertex:
        return v.word.lower().count('e')

class Filter:
    def __init__(self, regex, graph):
        self.regex = regex
        self.graph = graph
        print 'starting to compile filter...'
        print ' (%d nodes)' % self.regex.nnodes
        self.linop = regex.compile_into_linop()
        print 'done compiling filter!'

    def calculate_values(self):
        vals = np.ones(self.regex.nnodes)
        return self.linop.matvec(vals)

class FilterSet:
    def __init__(self, graph):
        self.graph = graph
        self.filters = {}
        self.vals = {}

    def add_filter(self, name, filt):
        self.filters[name] = filt
        

    def describe_node(self, node):
        # return " ".join("[%s=%f]" % (name, 
        #                              self.filters[name](node)) 
        #                 for name in self.filters)
        return " ".join("[%s=%f]" % (name, 
                                     self.vals[name][node.idx()])
                        for name in self.filters)

    
        
    def calculate_filters(self):
        print 'starting calculate_filters...'
        for name, filt in self.filters.items():
            self.vals[name] = filt.calculate_values()
        print 'done calculate_filters!'
