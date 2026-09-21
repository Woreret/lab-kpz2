from typing import Callable, Iterable, Iterator, TypeVar

from .pipeline import keep, normalize, parse

T = TypeVar("T")


def g_parse(lines: Iterable[str]) -> Iterator[dict]:
    for line in lines:
        rec = parse(line)
        if rec is not None:
            yield rec


def g_normalize(records: Iterable[dict]) -> Iterator[dict]:
    for rec in records:
        yield normalize(rec)


def g_keep(records: Iterable[dict], predicate: Callable[[dict], bool] = keep) -> Iterator[dict]:
    for rec in records:
        if predicate(rec):
            yield rec


def record_stream() -> Iterator[dict]:
    categories = ("Електроніка", "Книги", "Одяг")
    counter = 0
    while True:
        yield {"sku": f"ITEM-{counter:03}", "qty": counter % 25 + 1,
               "price": float(100 + counter % 10 * 20),
               "category": categories[counter % len(categories)]}
        counter += 1


def take(n: int, it: Iterable[T]) -> Iterator[T]:
    iterator = iter(it)
    for _ in range(n):
        try:
            item = next(iterator)
        except StopIteration:
            return
        yield item


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    iterator = iter(it)
    for _ in range(n):
        try:
            next(iterator)
        except StopIteration:
            return
    for item in iterator:
        yield item
