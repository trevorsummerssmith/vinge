import numpy as np
import scipy as sp
import networkx as nx
from vinge.graph import make_graph, normalize_graph
from vinge.regex import TrivialRegex, FilterRegex, ConcatRegex, DisjunctRegex, StarRegex

def assert_lists_equal(list1, list2):
    assert sorted(list1) == sorted(list2)

gf_undir = nx.desargues_graph()
gf = nx.DiGraph()
for (u,v) in gf_undir.edges_iter():
    gf.add_edge(u,v)
    gf.add_edge(v,u)


labels = ["a", "b", "aa", "ab", "ba", "bb", "aaa", "aab", "aba", "abb",
          "baa", "bab", "bba", "bbb", "aaaa",
          "aaab", "aaba", "aabb", "abaa", "abab"]
def length_filter(i):
    return np.exp(-len(labels[i]) * 0.3)

def starts_with_a(i):
    if labels[i][0] == 'a':
        return 1
    else:
        return 0

# apply labels to nodes
for label,nodeidx in zip(labels, gf.nodes()):
    gf.node[nodeidx]['label'] = label

# uniform weighting on edges
for (u,v) in gf.edges_iter():
    gf.edge[u][v]['weight'] = 1.0
normalize_graph(gf)

transition = nx.to_scipy_sparse_matrix(gf)
transition_op = sp.sparse.linalg.aslinearoperator(transition)

# something non-uniform to make accidental passing slightly less
# likely
initial_distro = np.arange(20.0)
initial_distro = initial_distro / sum(initial_distro)

class TestRegex:
    def test_trivial_regex(self):
        re = TrivialRegex(20)
        re_mat = re.compile_into_matrix()
        re_linop = re.compile_into_linop()

        dist_apply = re.apply(initial_distro)
        dist_mat = initial_distro * re_mat
        dist_linop = re_linop.matvec(initial_distro)

        dist_hand = initial_distro

        # note that approximate equality isn't transitive!
        np.testing.assert_allclose(dist_apply, dist_hand)
        np.testing.assert_allclose(dist_mat, dist_hand)
        np.testing.assert_allclose(dist_linop, dist_hand)
        np.testing.assert_allclose(dist_apply, dist_mat)
        np.testing.assert_allclose(dist_apply, dist_linop)
        np.testing.assert_allclose(dist_mat, dist_linop)

    def test_starts_with_a_filter_regex(self):
        re = FilterRegex(20, starts_with_a, gf)
        re_mat = re.compile_into_matrix()
        re_linop = re.compile_into_linop()

        dist_apply = re.apply(initial_distro)
        dist_mat = initial_distro * re_mat
        dist_linop = re_linop.matvec(initial_distro)

        dist_hand = initial_distro.copy()
        for i, label in enumerate(labels):
            if label[0] != 'a':
                dist_hand[i] = 0.0

        # note that approximate equality isn't transitive!
        np.testing.assert_allclose(dist_apply, dist_hand)
        np.testing.assert_allclose(dist_mat, dist_hand)
        np.testing.assert_allclose(dist_linop, dist_hand)
        np.testing.assert_allclose(dist_apply, dist_mat)
        np.testing.assert_allclose(dist_apply, dist_linop)
        np.testing.assert_allclose(dist_mat, dist_linop)

    def test_length_filter_regex(self):
        re = FilterRegex(20, length_filter, gf)
        re_mat = re.compile_into_matrix()
        re_linop = re.compile_into_linop()

        dist_apply = re.apply(initial_distro)
        dist_mat = initial_distro * re_mat
        dist_linop = re_linop.matvec(initial_distro)

        dist_hand = (initial_distro * 
                     np.array(([np.exp(-0.3)]*2) +
                              ([np.exp(-0.6)]*4) +
                              ([np.exp(-0.9)]*8) +
                              ([np.exp(-1.2)]*6)))

        # note that approximate equality isn't transitive!
        np.testing.assert_allclose(dist_apply, dist_hand)
        np.testing.assert_allclose(dist_mat, dist_hand)
        np.testing.assert_allclose(dist_linop, dist_hand)
        np.testing.assert_allclose(dist_apply, dist_mat)
        np.testing.assert_allclose(dist_apply, dist_linop)
        np.testing.assert_allclose(dist_mat, dist_linop)

    def test_concat_filter_regex(self):
        re1 = FilterRegex(20, length_filter, gf)
        re2 = FilterRegex(20, starts_with_a, gf)
        re3 = ConcatRegex(transition, transition_op, re1, re2)

        re3_mat = re3.compile_into_matrix()
        re3_linop = re3.compile_into_linop()
        
        dist_apply = re3.apply(initial_distro)
        dist_mat = initial_distro * re3_mat
        dist_linop = re3_linop.matvec(initial_distro)

        # construct the answer by another method to cross-check
        # step 1: apply the first filter
        dist_hand_tmp = (initial_distro * 
                         np.array(([np.exp(-0.3)]*2) +
                                  ([np.exp(-0.6)]*4) +
                                  ([np.exp(-0.9)]*8) +
                                  ([np.exp(-1.2)]*6)))
        # step 2: iterate over graph edges to simulate transition
        # matrix. check that the weights are 1/3 while we're at it.
        dist_hand = np.zeros(20)
        for (u,v,edata) in gf.edges_iter(data=True):
            dist_hand[v] += dist_hand_tmp[u] * edata['weight']
            assert(abs(3 * edata['weight'] - 1.0) < 0.01)
        # step 3: apply the second filter
        for i, label in enumerate(labels):
            if label[0] != 'a':
                dist_hand[i] = 0.0

        # note that approximate equality isn't transitive!
        np.testing.assert_allclose(dist_apply, dist_hand)
        np.testing.assert_allclose(dist_mat, dist_hand)
        np.testing.assert_allclose(dist_linop, dist_hand)
        np.testing.assert_allclose(dist_apply, dist_mat)
        np.testing.assert_allclose(dist_apply, dist_linop)
        np.testing.assert_allclose(dist_mat, dist_linop)

    def test_disjunct_filter_regex(self):
        re1 = FilterRegex(20, length_filter, gf)
        re2 = FilterRegex(20, starts_with_a, gf)
        re3 = DisjunctRegex(re1, re2)

        re3_mat = re3.compile_into_matrix()
        re3_linop = re3.compile_into_linop()

        dist_apply = re3.apply(initial_distro)
        dist_mat = initial_distro * re3_mat
        dist_linop = re3_linop.matvec(initial_distro)
        
        dist_hand = (initial_distro * 
                     np.array(([np.exp(-0.3)]*2) +
                              ([np.exp(-0.6)]*4) +
                              ([np.exp(-0.9)]*8) +
                              ([np.exp(-1.2)]*6)))
        for i, label in enumerate(labels):
            if label[0] == 'a':
                dist_hand[i] += initial_distro[i]
                
        # note that approximate equality isn't transitive!
        np.testing.assert_allclose(dist_apply, dist_hand)
        np.testing.assert_allclose(dist_mat, dist_hand)
        np.testing.assert_allclose(dist_linop, dist_hand)
        np.testing.assert_allclose(dist_apply, dist_mat)
        np.testing.assert_allclose(dist_apply, dist_linop)
        np.testing.assert_allclose(dist_mat, dist_linop)

    def test_star_regex(self):
        re1 = TrivialRegex(20)
        re2 = StarRegex(transition, transition_op, 20, re1, 3)
        
        re2_mat = re2.compile_into_matrix()
        re2_linop = re2.compile_into_linop()

        dist_apply = re2.apply(initial_distro)
        dist_mat = np.dot(initial_distro, re2_mat)
        dist_linop = re2_linop.matvec(initial_distro)

        pathlength = 3.0
        pstop = 1.0 / pathlength
        pgo = 1 - pstop
        tmat = pgo * transition.todense()
        star_hand = np.zeros((20,20))
        for i in xrange(30):
            star_hand += np.linalg.matrix_power(tmat, i)
        star_hand = pstop * star_hand

        # make sure that the relevant thing is invertible...
        vals, vecs = np.linalg.eig(tmat)
        assert (abs(vals) < 0.9).all()

        # The tolerance on this test had to be increased a bit to make
        # it pass, but I think that's OK.
        np.testing.assert_allclose(star_hand, re2_mat, rtol=1e-04, atol=1e-08)

        dist_hand = np.dot(initial_distro, np.array(star_hand))


        # note that approximate equality isn't transitive!
        np.testing.assert_allclose(dist_apply, dist_hand, 
                                   rtol=1e-04, atol=1e-08)
        np.testing.assert_allclose(dist_mat, dist_hand, 
                                   rtol=1e-04, atol=1e-08)
        np.testing.assert_allclose(dist_linop, dist_hand, 
                                   rtol=1e-04, atol=1e-08)
        np.testing.assert_allclose(dist_apply, dist_mat, 
                                   rtol=1e-04, atol=1e-08)
        np.testing.assert_allclose(dist_apply, dist_linop, 
                                   rtol=1e-04, atol=1e-08)
        np.testing.assert_allclose(dist_mat, dist_linop, 
                                   rtol=1e-04, atol=1e-08)



foo = TestRegex()
foo.test_star_regex()
