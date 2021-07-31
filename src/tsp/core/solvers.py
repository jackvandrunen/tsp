"""Implements random, optimal, and human-approximate solvers.

Other solvers can be implemented by extending `Solver`, which functions as an abstract class. Due
to a historical contingency in the depths of the past, the API is somewhat opaque, and it's
questionable whether we might have been better off if the solvers weren't object-oriented. The
basic idea is that the initializer sets up the solver, and then the `__call__` method is what does
the computation and returns the tour. So, `Solver.__init__` and `Solver.__call__` should be
overridden by subclasses - while `Solver.solve` is a newer addition serving as syntactical sugar
for `Solver.__call__`.

The random solver is exactly as advertised - returning a random permutation of the cities as a
solution.

The optimal solver uses the [Concorde](https://www.math.uwaterloo.ca/tsp/concorde.html) backend.
Sadly, Concorde can be a difficult thing to get working on a machine, but it is the gold standard
in cognitive science research on TSP. Once you have Concorde installed, it is much easier using
this library to find optimal tours than using Concorde directly.

The human-approximate solver uses a hierarchical clustering ("pyramid") algorithm implemented in the
`tsp.core.pyramid` submodule.
"""


import os
from numpy.typing import NDArray
import numpy as np
from pytsp import dumps_matrix, run as run_concorde

from tsp.core.tsp import N_TSP
from tsp.core.pyramid import pyramid_solve


class Solver:
    """Abstract class for generic TSP solvers."""

    def __init__(self, tsp: N_TSP):
        """Set up the solver based on the given problem.

        Args:
            tsp (N_TSP): problem to be solved.
        """

    def __call__(self) -> NDArray:
        """Run the solver and produce a tour.

        Returns:
            NDArray: tour as indices of cities
        """
        raise NotImplementedError

    def solve(self) -> NDArray:
        """Run the solver and produce a tour.

        Returns:
            NDArray: tour as indices of cities
        """
        return self()


class RandomSolver(Solver):
    """A solver which produces a random tour."""

    def __init__(self, tsp: N_TSP):
        Solver.__init__(self, tsp)
        self.vertices = np.arange(tsp.cities.shape[0])

    def __call__(self) -> NDArray:
        np.random.shuffle(self.vertices)
        return self.vertices


class ConcordeSolver(Solver):
    """An optimal solver with the Concorde backend."""

    def __init__(self, tsp: N_TSP):
        Solver.__init__(self, tsp)
        E = tsp.to_edge_matrix()
        self.outf = './tsp.temp'
        with open(self.outf, 'w') as dest:
            dest.write(dumps_matrix(E))

    def __call__(self) -> NDArray:
        old_dir = os.getcwd()
        tour = run_concorde(self.outf, start=0, solver="concorde")
        os.unlink(self.outf)
        os.chdir(old_dir)
        return np.array(tour['tour'])


class PyramidSolver(Solver):
    """A solver which implements a pyramid approximator."""

    def __init__(self, tsp: N_TSP):
        Solver.__init__(self, tsp)
        self.m = tsp.to_matrix()

    def __call__(self) -> NDArray:
        return np.array(pyramid_solve(self.m))
