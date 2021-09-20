from functools import reduce
from typing import Callable, Any


def pipeline(*funcs: Callable) -> Callable:
    def _reducer(func1, func2):
        try:
            return lambda *x: func2(func1(*x))
        except Exception as e:
            raise e

    return reduce(_reducer, funcs)


def fork(*funcs: Callable) -> Callable:
    return lambda *x: [func(*x) for func in funcs]


def merge(func: Callable[[Any, Any], Any]) -> Callable:
    return lambda branches: reduce(lambda x, y: func(x, y), branches)


def identity():
    lambda x: x