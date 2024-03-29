"""Helper functions for saving and loading sets of problems and tours.

The experiment code relies on files saved in a particular format in a root directory. Files should
be named according to the "001.x" convention where numbering starts from 1 and "x" substitutes for
the appropriate file extension. The `save_problem_batch` and `load_problem_batch` procedures handle
this for TSPs of any kind from `tsp.core` or `tsp.extra`, saving them with the ".tsp" extension.

`save_list_batch` and `load_list_batch` handle this for anything that can be saved with
`tsp.core.save.save_list`. `save_list_item` is for saving an individual list with the proper
numbering format. Examples of sequences that are saved using these procedures are tours (human and
model-generated) and the times for human tours. Tours are saved using the ".sol" extension, and
times using the ".time" extension. See `tsp.experiment.batch_server` for more on the data the UI
for human-subject experiments collects.
"""


from typing import Any, Iterable, List
import glob
import os

from tsp.extra.save import load_problem, save_problem, load_list, save_list


def save_problem_batch(objs: Iterable[Any], path: str, starting_index: int = 1):
    """Serialize a batch of problems, following the numbering format `001.tsp`, etc.
    Can handle any N_TSP descendant from tsp.core or tsp.extra.

    Args:
        objs (Iterable[Any]): problems
        path (str): root to save in
        starting_index (int, optional): Starting index for numbering. Defaults to 1.
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    for i, tsp in enumerate(objs, starting_index):
        save_problem(tsp, os.path.join(path, f'{str(i).zfill(3)}.tsp'))


def load_problem_batch(path: str) -> Iterable[Any]:
    """Unserialize a batch of problems.
    Can handle any N_TSP descendant from tsp.core or tsp.extra.

    Args:
        path (str): root to load from

    Returns:
        Iterable[Any]: problems
    """
    result = []
    for path_ in sorted(glob.glob(os.path.join(path, '*.tsp'))):
        result.append(load_problem(path_))
    return result


def save_list_item(obj: Iterable[Any], path: str, ext: str, index: int):
    """Generic save function wrapping tsp.core.save.save_list.
    Serializes tour/sequence to a file with format, e.g., `001.ext` if index is 1.

    Args:
        obj (Iterable[Any]): list
        path (str): root to save in
        ext (str): file extension to save as
        index (int): index
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    save_list(obj, os.path.join(path, f'{str(index).zfill(3)}.{ext}'))


def save_list_batch(objs: Iterable[Iterable[Any]], path: str, ext: str, starting_index: int = 1):
    """Generic save function for batch of tours/sequences.
    Serializes following the numbering format `001.ext`, etc.

    Args:
        objs (Iterable[Iterable[Any]]): lists
        path (str): root to save in
        ext (str): file extension to save as
        starting_index (int, optional): Starting index for numbering. Defaults to 1.
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    for i, obj in enumerate(objs, starting_index):
        save_list_item(obj, path, ext, i)


def load_list_batch(path: str, ext: str) -> List[List[Any]]:
    """Generic load function for batch of tours/sequences.

    Args:
        path (str): root to load from
        ext (str): file extension to load

    Returns:
        List[List[Any]]: lists
    """
    result = []
    for path_ in sorted(glob.glob(os.path.join(path, f'*.{ext}'))):
        result.append(load_list(path_))
    return result
