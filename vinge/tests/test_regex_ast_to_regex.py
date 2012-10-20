import networkx as nx
import scipy as sp

import vinge.filters
from vinge.regex_ast_to_regex import ast_to_regex
from vinge.regex_parser import *
from vinge.semex.semex import *
from vinge.vertex import LogLineVertex, UniqueIDVertex

# Don't care about this graph structure at all.
# Just need something to plumb the tests together.
graph = nx.DiGraph()
v1 = LogLineVertex("hello", "hello", 1, "threadid", 6)
v2 = UniqueIDVertex("ok!")
graph.add_edge(v1, v2)
transition = nx.to_scipy_sparse_matrix(graph)
transition_op = sp.sparse.linalg.aslinearoperator(transition)

def do_ast_to_regex(ast):
    return ast_to_regex(graph, transition, transition_op, ast)

class TestRegexAstToRegex:

    def test_any(self):
        ast = BaseAbsyn(BaseType.ANYTHING)
        regex = do_ast_to_regex(ast)
        assert regex == TrivialRegex(graph.number_of_nodes())

    def test_logline(self):
        ast = BaseAbsyn(BaseType.LOGLINE)
        regex = do_ast_to_regex(ast)
        assert regex == FilterRegex(graph.number_of_nodes(),
                                    vinge.filters.logline,
                                    graph)

    def test_tag(self):
        ast = BaseAbsyn(BaseType.TAG)
        regex = do_ast_to_regex(ast)
        assert regex == FilterRegex(graph.number_of_nodes(),
                                    vinge.filters.tag,
                                    graph)

    def test_id(self):
        ast = BaseAbsyn(BaseType.ID)
        regex = do_ast_to_regex(ast)
        assert regex == FilterRegex(graph.number_of_nodes(),
                                    vinge.filters.id,
                                    graph)

    def test_concat(self):
        ast = ConcatAbsyn(BaseAbsyn(BaseType.LOGLINE), BaseAbsyn(BaseType.ID))
        regex = do_ast_to_regex(ast)
        answer = ConcatRegex(transition, transition_op,
                             FilterRegex(graph.number_of_nodes(),
                                         vinge.filters.logline,
                                         graph),
                             FilterRegex(graph.number_of_nodes(),
                                         vinge.filters.id,
                                         graph)
                             )
        assert regex == answer

    def test_disjunct(self):
        ast = DisjunctAbsyn(BaseAbsyn(BaseType.ID), BaseAbsyn(BaseType.TAG))
        regex = do_ast_to_regex(ast)
        answer = DisjunctRegex(FilterRegex(graph.number_of_nodes(),
                                           vinge.filters.id,
                                           graph),
                               FilterRegex(graph.number_of_nodes(),
                                           vinge.filters.tag,
                                           graph)
                               )
        assert regex == answer

    def test_star(self):
        ast = StarAbsyn(BaseAbsyn(BaseType.ANYTHING))
        regex = do_ast_to_regex(ast)
        answer= StarRegex(transition, transition_op,
                          graph.number_of_nodes(),
                          TrivialRegex(graph.number_of_nodes()),
                          length=3.0)
        assert regex == answer
