from functools import reduce
from math import isfinite
from typing import Callable, Iterable, Iterator

from .hof import make_predicate, pipe
from .model import Result


def parse(line: str) -> dict | None:
    fields = line.rstrip("\r\n").split(";")
    if len(fields) != 4 or any(not field.strip() for field in fields):
        return None
    sku, qty, price, category = fields
    try:
        int(qty)
        price_value = float(price)
    except ValueError:
        return None
    if not isfinite(price_value):
        return None
    return {"sku": sku, "qty": qty, "price": price_value, "category": category}


def process(lines: Iterable[str], now: float) -> Result:
    records = []
    errors = 0
    for line in lines:
        rec = parse(line)
        if rec is None:
            errors += 1
        else:
            records.append({**rec, "received_at": now})
    return Result(tuple(records), errors)


def strip_strings(rec: dict) -> dict:
    return {key: value.strip() if isinstance(value, str) else value
            for key, value in rec.items()}


def lower_category(rec: dict) -> dict:
    return {**rec, "category": rec["category"].lower()}


def to_int_number(rec: dict) -> dict:
    return {**rec, "qty": int(rec["qty"])}


normalize: Callable[[dict], dict] = pipe(strip_strings, lower_category, to_int_number)
keep: Callable[[dict], bool] = make_predicate("qty", "ge", 5)


def add_to_groups(acc: dict[str, int], rec: dict) -> dict[str, int]:
    category = rec["category"]
    return {**acc, category: acc.get(category, 0) + rec["qty"]}


def aggregate(records: Iterable[dict]) -> dict[str, int]:
    return reduce(add_to_groups, records, {})


def select_records(lines: Iterable[str], predicate: Callable[[dict], bool] = keep) -> Iterator[dict]:
    parsed = map(parse, lines)
    valid = filter(lambda rec: rec is not None, parsed)
    normalized = map(normalize, valid)
    return filter(predicate, normalized)


def pipeline(lines: Iterable[str], predicate: Callable[[dict], bool] = keep) -> dict[str, int]:
    return aggregate(select_records(lines, predicate))
