.. title:: Semiotic Expressions

====================
Semiotic Expressions
====================

We wish to manipulate probability distributions and other weightings
over the nodes of a Markov chain. We also wish to represent
probability distributions and other weightings over sets of paths
through the Markov chain.

Weighted pathsets are naturally represented as linear operators over
distributions: consider a matrix A, where the entry A_{ij} gives the
total weight of paths in the path set which start at node #i and end
at node #j. Multiplying such matrices then correctly concatenates all
compatible paths from two path sets. 

Semexes ("semiotic expressions") are an intuitive way to specify such
linear operators.

======================================
A cautionary note about linear algebra
======================================

Linear algebra is a treacherous subject because it can be done in two
equivalent ways, with row vectors multiplied by matrices on their
right, or column vectors multiplied by matrices on their left. For the
sake of clarity, let us consider only row vectors. (Note that this is
only sort of clear; in particular, concatenation of semexes is the
reverse of the corresponding matrix multiplication.) In the code
below, we use both versions, because this lets us use important
functionality (linear operators) from scipy. We will put a comment
whenever we break this convention.

================
Building Semexes
================

Semexes are implemented as follows. This can be thought of as a
weighted version of the Thompson NFA algorithm for implementing
regular expression search [1, but see 2 for an exposition intelligible
to the modern reader].

- A sensor is a function f from nodes to R (the reals), representing a
  set of paths of length zero (i.e., paths containing a single node
  and no edges). As a linear operator, it sends d[i] to f(node_i) *
  d[i]. Sensors correspond to diagonal matrices.

  Sensors can be thought of as the emission probabilities of a
  time-dependent HMM.

- Disjunction (semex | semex) is the union of two path sets. As a
  linear operator, this is implemented as the sum of the constituent
  linear operators. Note that this causes double counting if the
  choices overlap. We posit that such double counting is not a major
  concern, but users should be aware of this when crafting semiotic
  expressions.

- The Kleene star (sensor semex length *) is the set of all paths of
  any length, weighted by the sensor at the nodes and the semex at the
  edges. For technical reasons, we require the user to specify a
  desired length. The semex will match paths of any length, but it
  will prefer paths of roughly the specified length.

- Concatentation (semex sensor semex) represents the set of paths
  formable by joining any path from the first path set with any path
  from the second path set. The sensor specifies a weighting based on
  the node used to join the paths.

  This is implemented as the product of three linear operators: the
  linear operator of the first operand, the sensor operator, and the
  linear operator of the second operand.

==================
Compiling Semexes 
==================

Semexes can be compiled, either into a matrix (implemented as a scipy
sparse matrix when possible, and as a numpy matrix otherwise) or into
a scipy LinearOperator, which should be far more efficient. The
LinearOperators are the transposes of the matrices, since
LinearOperators are designed to be used like (x -> Ax) rather than (x
-> xA). The second fits more naturally with Markov chains and the
semantics of semiotic expressions.

==========
References
==========

[1] Ken Thompson, "Regular expression search algorithm",
Communications of the ACM 11(6) (June 1968),
pp. 419-422. http://doi.acm.org/10.1145/363347.363387 (PDF)

[2] Russ Cox, "Regular Expression Matching Can Be Simple And Fast",
January 2007, http://swtch.com/~rsc/regexp/regexp1.html
