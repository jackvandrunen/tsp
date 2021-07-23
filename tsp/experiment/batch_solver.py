from typing import Callable, List, Tuple, Union
from numpy.typing import ArrayLike, NDArray
import numpy as np

from tsp.core.tsp import N_TSP
from tsp.core.solvers import Solver
from tsp.experiment.batch import load_list_batch, load_problem_batch, save_list_batch


def solve_batch(src: str, solver: Solver, dest: str = None) -> List[List[int]]:
    """Use a solver to generate tours for a batch of problems.

    Args:
        src (str): path of root where problems are saved
        solver (Solver): an instance of a Solver (tsp.core.solvers.Solver)
        dest (str, optional): Path of root to save tours. Defaults to None.

    Returns:
        List[List[int]]: tours
    """
    batch = load_problem_batch(src)
    tours = []
    for p in batch:
        tours.append(solver(p)())
    if dest is not None:
        save_list_batch(tours, dest, 'sol')
    return tours


def score_tours_absolute(problems: List[N_TSP], tours: List[Union[int, ArrayLike]]) -> NDArray:
    """Calculate tour lengths for a batch of tours.

    Args:
        problems (List[N_TSP]): list of TSPs
        tours (List[Union[int, ArrayLike]]): list of tours (in either index or segment format)

    Returns:
        NDArray: tour lengths
    """
    result = np.ndarray((len(problems),), dtype=np.float)
    for i, (p, t) in enumerate(zip(problems, tours)):
        result[i] = p.score(t)
    return result


def score_batch(problems_path: str, tours_path: str) -> NDArray:
    """Calculate tour lengths for a batch of tours, for use on serialized problems and tours.

    Args:
        problems_path (str): path of root where problems are saved
        tours_path (str): path of root where tours are saved

    Returns:
        NDArray: tour lengths
    """
    problems = load_problem_batch(problems_path)
    tours = load_list_batch(tours_path, 'sol')
    return score_tours_absolute(problems, tours)


def score_tours_relative(problems: List[N_TSP], tours: List[Union[int, ArrayLike]], base_tours: List[Union[int, ArrayLike]]) -> Tuple[NDArray, float, float]:
    """Calculate tour errors relative to reference tours (for example, the optimal tours solved by Concorde).

    Args:
        problems (List[N_TSP]): list of TSPs
        tours (List[Union[int, ArrayLike]]): list of tours (in either index or segment format)
        base_tours (List[Union[int, ArrayLike]]): list of reference tours (in either index or segment format)

    Returns:
        Tuple[NDArray, float, float]: (proportional errors, mean error, standard error of mean)
    """
    errors = np.ndarray((len(problems),), dtype=np.float)
    for i, (p, t, b) in enumerate(zip(problems, tours, base_tours)):
        tour_score = p.score(t)
        base_score = p.score(b)
        errors[i] = (tour_score / base_score) - 1.
    return errors, np.mean(errors), np.std(errors) / np.sqrt(len(errors))


def score_batch_2(problems_path: str, tours_path: str, base_tours_path: str) -> Tuple[NDArray, float, float]:
    """Calculate tour errors relative to reference tours, for use on serialized problems and tours.

    Args:
        problems_path (str): path of root where problems are saved
        tours_path (str): path of root where tours are saved
        base_tours_path (str): path of root where reference tours are saved

    Returns:
        Tuple[NDArray, float, float]: (proportional errors, mean error, standard error of mean)
    """
    problems = load_problem_batch(problems_path)
    tours = load_list_batch(tours_path, 'sol')
    base = load_list_batch(base_tours_path, 'sol')
    return score_tours_relative(problems, tours, base)


def _load_all_tour_segments_to_indices(problems: N_TSP, tours_path: str) -> Callable:
    tours = load_list_batch(tours_path, 'sol')
    result = []
    for problem, tour in zip(problems, tours):
        result.append(problem.convert_tour_segments(tour))
    return result


def score_batch_3(problems_path: str, tours_path: str, base_tours_path: str) -> Tuple[NDArray, float, float]:
    """Calculate tour errors relative to reference tours, for use on serialized problems and tours.
    Expects serialized tours (in tours_path) to be in segment format (i.e., generated by a human subject),
    and converts them to index format.
    Unless you're doing specialized work with the TSP_O library, you probably don't need this.

    Args:
        problems_path (str): path of root where problems are saved
        tours_path (str): path of root where tours are saved (in segment format)
        base_tours_path (str): path of root where reference tours are saved

    Returns:
        Tuple[NDArray, float, float]: (proportional errors, mean error, standard error of mean)
    """
    problems = load_problem_batch(problems_path)
    tours = _load_all_tour_segments_to_indices(problems, tours_path)
    base = load_list_batch(base_tours_path, 'sol')
    return score_tours_relative(problems, tours, base)
