from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Result:
    records: tuple[dict, ...]
    errors: int


@dataclass(frozen=True, slots=True)
class Record:
    sku: str
    qty: int
    price: float
    category: str
    received_at: float


def to_record(d: dict) -> Record:
    return Record(**d)


def add_qty(record: Record, amount: int) -> Record:
    return replace(record, qty=record.qty + amount)


def change_sku(record: Record, sku: str) -> Record:
    return replace(record, sku=sku)
