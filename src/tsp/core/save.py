"""Procedures for serializing TSP objects and tours.

Prefer `save_problem` and `load_problem` over `save_ntsp`, etc. These are general-purpose
procedures which determine the type of the problem and the proper procedure for serialization.
Note also that `tsp.extra.save.save_problem` and `tsp.extra.save.load_problem` work on a strict
*superset* of the problem types handled by `save_problem` and `load_problem`, so can be dropped
in for these seamlessly.

Use `save_list` and `load_list` to serialize and unserialize tours. The conventional extension for
tours is `.sol` (for "solution").

See `tsp.experiment.batch` for procedures for serializing whole sets of problems and tours.
"""


from typing import Any, Dict, Iterable, List
import json
import numpy as np

from tsp.core.tsp import N_TSP, TSP


class LoadError(Exception):
    """Exception for expected problems with loading files."""


def save_ntsp(obj: N_TSP, path: str):
    """Serialize an N_TSP object.

    Args:
        obj (N_TSP): object
        path (str): path to save
    """
    struct = {
        "type": "N_TSP",
        "cities": obj.cities.tolist()
    }
    with open(path, 'w') as f:
        json.dump(struct, f)


def _load_ntsp(struct: Dict) -> N_TSP:
    return N_TSP.from_cities(struct["cities"])


def load_ntsp(path: str) -> N_TSP:
    """Unserialize an N_TSP object.

    Args:
        path (str): path to load

    Returns:
        N_TSP: object
    """
    with open(path, 'r') as f:
        struct = json.load(f)
    return _load_ntsp(struct)


def save_tsp(obj: TSP, path: str):
    """Serialize a TSP object.

    Args:
        obj (TSP): object
        path (str): path to save
    """
    struct = {
        "type": "TSP",
        "cities": obj.cities.tolist(),
        "w": obj.w,
        "h": obj.h
    }
    with open(path, 'w') as f:
        json.dump(struct, f)


def _load_tsp(struct: Dict) -> TSP:
    return TSP.from_cities(struct["cities"], struct["w"], struct["h"])


def load_tsp(path: str) -> TSP:
    """Unserialize a TSP object.

    Args:
        path (str): path to load

    Returns:
        TSP: object
    """
    with open(path, 'r') as f:
        struct = json.load(f)
    return _load_tsp(struct)


def save_problem(obj: Any, path: str):
    """Serialize an object (should be descended from N_TSP).

    Args:
        obj (Any): object
        path (str): path to save
    """
    if isinstance(obj, TSP):
        save_tsp(obj, path)
    else:
        save_ntsp(obj, path)  # try to save anything else as if it's a generic N_TSP


def load_problem(path: str) -> Any:
    """Unserialize an object (TSP or N_TSP).

    Args:
        path (str): path to load

    Raises:
        LoadError: serialized object not TSP or N_TSP

    Returns:
        Any: object
    """
    with open(path, 'r') as f:
        struct = json.load(f)
    if struct["type"] == "TSP":
        return _load_tsp(struct)
    if struct["type"] == "N_TSP":
        return _load_ntsp(struct)
    raise LoadError('invalid type')


def save_list(obj: Iterable[Any], path: str):
    """Generic save function for tours/sequences of various formats.

    Args:
        obj (Iterable[Any]): list
        path (str): path to save
    """
    with open(path, 'w') as f:
        json.dump(obj.tolist() if isinstance(obj, np.ndarray) else list(obj), f)


def load_list(path: str) -> List[Any]:
    """Generic load function for tours/sequences of various formats.

    Args:
        path (str): path to load

    Returns:
        List[Any]: list
    """
    with open(path, 'r') as f:
        return json.load(f)
