"""
A regex is:
filter
regex | regex
regex *
regex regex

We wish to manipulate probability distributions over the nodes of a
Markov chain. We also want to represent sets of weighted paths through
the Markov chain, which are naturally represented as linear operators
over distributions. Regexes are an intuitive way to specify such
linear operators.

Regexes are implemented as follows. This can be thought of as a
generalization of the Thompson NFA algorithm for implementing regular
expression search [1, but see 2 for an exposition intelligible to the
modern reader].

  - A filter is a function f from nodes to R, representing a set of
    paths of length zero (i.e., paths containing a single node and no
    edges). As a linear operator, it sends d[i] to f(node_i) *
    d[i]. Filters correspond to diagonal matrices.

  - Disjunction (regex | regex) is the union of two path sets. As a
    linear operator, this is implemented as the sum of the constituent
    linear operators. Note that this causes double counting if the
    choices overlap. We posit that such double counting is not a major
    concern, but users should be aware of this when crafting regular
    expressions.

  - The Kleene star ... got lazy writing this ...

  - Concatentation (regex regex) represents the set of paths formable
    by concatenating any path from the first path set with any path
    from the second path set. This is implemented as the product of
    the constituent linear operators.

Regexes can be compiled, either into a matrix (implemented as a scipy
sparse matrix when possible) or into a scipy LinearOperator.

References:

[1] Ken Thompson, “Regular expression search algorithm,”
Communications of the ACM 11(6) (June 1968),
pp. 419–422. http://doi.acm.org/10.1145/363347.363387 (PDF)

[2] Russ Cox, “Regular Expression Matching Can Be Simple And Fast”,
January 2007, http://swtch.com/~rsc/regexp/regexp1.html
"""

import numpy as np
import networkx as nx
import scipy as sp
from scipy.sparse.linalg import LinearOperator, aslinearoperator

# TODO make this a proper abstract class
class Regex:
    def compile_into_matrix(self):
        raise NotImplemented

    def compile_into_linop(self):
        raise NotImplemented

    def apply(self, dist):
        raise NotImplemented

class FilterRegex(Regex):
    def __init__(self, nnodes, thefilter):
        ''' thefilter: maps integer ids to reals
        '''
        self.nnodes = nnodes 
        self.thefilter = thefilter

    def compile_into_matrix(self):
        filter_values = np.zeros(self.nnodes)
        for i in xrange(self.nnodes):
            filter_values[i] = self.thefilter(i)
        return sp.sparse.diags(filter_values, [0])

    def compile_into_linop(self):
        return LinearOperator((self.nnodes,self.nnodes), matvec=self.apply)

    def apply(self, dist):
        dist2 = np.zeros(len(dist))
        for i in xrange(len(dist)):
            dist2[i] = dist[i] * thefilter(i)
        return dist2

class DisjunctRegex(Regex):
    def __init__(self, poss1, poss2):
        self.poss1 = poss1
        self.poss2 = poss2

    def compile_into_matrix(self):
        mat1 = self.poss1.compile_into_matrix()
        mat2 = self.poss2.compile_into_matrix()
        return mat1 + mat2

    def compile_into_linop(self):
        op1 = self.poss1.compile_into_linop()
        op2 = self.poss2.compile_into_linop()
        return op1 + op2

    def apply(self, dist):
        dist1 = self.poss1.apply(dist)
        dist2 = self.poss1.apply(dist)
        return dist1 + dist2

class StarRegex(Regex):
    def __init__(self, nnodes, inside, length):
        self.nnodes = nnodes
        self.inside = inside
        self.length = length
        self.p = 1.0 / self.length

    def compile_into_matrix(self):
        # build inverse of matrix
        inside = self.inside.compile_into_matrix()
        eye = sp.sparse.eye(self.nnodes, self.nnodes)
        invmat = (eye - self.p * inside) / (1-self.p)

        # then invert
        return np.linalg.inv(invmat)

    def compile_into_linop(self):
        # build inverse of the operator
        inside = self.inside.compile_into_linop()
        eye = aslinearoperator(sp.sparse.eye(self.nnodes, self.nnodes))
        invop = (eye - self.p * inside) / (1-self.p)

        # guess the inverse of the inverse of the operator (i.e.,
        # approximate the operator)
        precond = (eye + self.p * inside) / (1-self.p)

        def matvec(v):
            # get the operator by using conjugate gradient iteration
            # to find inverse of inverse
            x,info = sp.sparse.linalg.cg(inside, v, M=precond)
            assert(info == 0)
            return x

        return LinearOperator((self.nnodes,self.nnodes), matvec=matvec)

    def apply(self, dist):
        linop = self.compile_into_linop()
        return linop.matvec(dist)

class ConcatRegex(Regex):
    def __init__(self, part1, part2):
        self.part1 = part1
        self.part2 = part2

    def compile_into_matrix(self):
        mat1 = self.part1.compile_into_matrix() 
        mat2 = self.part2.compile_into_matrix()
        return mat1 * mat2

    def compile_into_linop(self):
        op1 = self.part1.compile_into_linop() 
        op2 = self.part2.compile_into_linop()
        return op1 * op2

    def apply(self, dist):
        dist2 = self.part2.apply(dist)
        return self.part1.apply(dist2)
