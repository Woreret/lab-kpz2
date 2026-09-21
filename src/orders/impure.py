import time
from pathlib import Path

from .pipeline import parse

records: list[dict] = []
errors = 0


def load(path: str | Path) -> None:
    global errors
    with open(path, encoding="utf-8") as lines:
        for line in lines:
            print("Читаю:", line.rstrip())
            rec = parse(line)
            if rec is None:
                errors += 1
                continue
            rec["received_at"] = time.time()
            records.append(rec)
