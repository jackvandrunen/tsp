import argparse
import json
from pathlib import Path
from pickle import UnpicklingError
import numpy as np

from tsp.batch import load, load_obstacles, load_tour, load_tour_segments


def load_stress(path):
    with open(path, 'r') as f:
        return [float(f.read().strip())]


def save_problem(obj, path):
    if 'obstacles' in obj.__dict__ and len(obj.obstacles) > 0:
        struct = {
            'type': 'TSP_O',
            'cities': obj.cities.tolist() if isinstance(obj.cities, np.ndarray) else list(obj.cities),
            'w': obj.w,
            'h': obj.h,
            'obstacles': obj.obstacles.tolist() if isinstance(obj.obstacles, np.ndarray) else list(obj.obstacles)
        }
    elif 'colors' in obj.__dict__:
        struct = {
            'type': 'TSP_Color',
            'cities': obj.cities.tolist() if isinstance(obj.cities, np.ndarray) else list(obj.cities),
            'w': obj.w,
            'h': obj.h,
            'colors': obj.colors.tolist() if isinstance(obj.colors, np.ndarray) else list(obj.colors)
        }
    elif 'w' in obj.__dict__:
        struct = {
            'type': 'TSP',
            'cities': obj.cities.tolist() if isinstance(obj.cities, np.ndarray) else list(obj.cities),
            'w': obj.w,
            'h': obj.h
        }
    else:
        struct = {
            'type': 'N_TSP',
            'cities': obj.cities.tolist() if isinstance(obj.cities, np.ndarray) else list(obj.cities)
        }
    with open(path, 'w') as f:
        json.dump(struct, f)


def save_list(obj, path):
    """Generic save function for tours/sequences of various formats.
    Args:
        obj (Iterable[Any]): list
        path (str): path to save
    """
    with open(path, 'w') as f:
        json.dump(obj.tolist() if isinstance(obj, np.ndarray) else list(obj), f)


def run(root):
    """Convert:
     - .tsp
     - .sol
     - .stress
     - .time shouldn't need to be converted because already JSON :)
    """
    for path in Path(root).rglob('*.tsp'):
        try:
            print(path)
            obj = None
            try:
                obj = load(path)
            except Exception:
                obj = load_obstacles(path)
            save_problem(obj, path)
        except UnpicklingError:
            print('Skipping...')

    for path in Path(root).rglob('*.sol'):
        try:
            print(path)
            obj = None
            try:
                obj = load_tour(path)
            except Exception:
                obj = load_tour_segments(path)
            save_list(obj, path)
        except UnpicklingError:
            print('Skipping...')
    
    for path in Path(root).rglob('*.stress'):
        try:
            print(path)
            obj = load_stress(path)
            save_list(obj, path)
        except ValueError:
            print('Skipping...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recursively convert a project to use the new API in place.')
    parser.add_argument('path', type=str, help='The root to be converted.')
    args = parser.parse_args()

    run(args.path)
