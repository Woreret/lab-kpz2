import operator
from typing import Any, Callable


def compose2(f: Callable, g: Callable) -> Callable:
    return lambda x: f(g(x))


def pipe(*funcs: Callable) -> Callable:
    def apply(value: Any) -> Any:
        for func in funcs:
            value = func(value)
        return value
    return apply


def compose(*funcs: Callable) -> Callable:
    return pipe(*reversed(funcs))


def make_predicate(field: str, op: str, value: Any) -> Callable[[dict], bool]:
    operation = getattr(operator, op)
    return lambda rec: operation(rec[field], value)


def make_running_total() -> Callable[[int], int]:
    total = 0

    def add(value: int) -> int:
        nonlocal total
        total += value
        return total
    return add


def scale(factor: float, value: float) -> float:
    return round(factor * value, 2)


def curry3(f: Callable) -> Callable:
    return lambda a: lambda b: lambda c: f(a, b, c)
