"""ЛР №2, варіант 3. Запуск: python demo.py (Python 3.10+)."""
import sys
import time
from dataclasses import FrozenInstanceError, dataclass
from functools import partial
from itertools import islice
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from orders.calculator import Add, Div, Mul, Neg, Num, Pow, Sqrt, Sub, Sum, evaluate
from orders.hof import compose, compose2, curry3, make_predicate, make_running_total, pipe, scale
from orders.lazy import drop, g_keep, g_normalize, g_parse, record_stream, take
from orders.model import add_qty, change_sku, to_record
from orders.pipeline import (
    aggregate, keep, lower_category, normalize, pipeline, process,
    select_records, strip_strings, to_int_number,
)


def main() -> None:
    path = Path(__file__).resolve().parent / "data" / "orders.txt"
    with open(path, encoding="utf-8") as file:
        lines = file.readlines()

    print("1. Чисті функції")
    res1 = process(lines, now=1000.0)
    res2 = process(lines, now=1000.0)
    print("Однакові результати:", res1 == res2)
    print("Рядків:", len(lines), "Коректних:", len(res1.records), "Помилок:", res1.errors)
    print("Після повторного виклику записів:", len(res2.records))
    print("Порожній вхід після повного:", process([], now=1000.0))
    current = process(lines, now=time.time())
    print("Час передано з main:", current.records[0]["received_at"])

    print("\n2. Незмінний запис")
    record = to_record(normalize(res1.records[0]))
    try:
        record.qty = 100
    except FrozenInstanceError as error:
        print("Змінити поле не можна:", error)
    print("Додали кількість:", add_qty(record, 5))
    print("Змінили SKU:", change_sku(record, "USB-NEW"))
    print("Початковий запис:", record)
    print("Set:", {record})
    print("Ключ словника:", {record: "замовлення"}[record])

    @dataclass
    class MutableRecord:
        sku: str
        qty: int
        price: float
        category: str
        received_at: float

    try:
        print({MutableRecord(record.sku, record.qty, record.price, record.category, record.received_at)})
    except TypeError as error:
        print("Звичайний dataclass нехешований:", error)

    print("\n3. Функції вищого порядку та замикання")
    f, g, h = lambda x: x + 1, lambda x: x * 2, lambda x: x ** 2
    print("compose2:", compose2(f, g)(3), "=", f(g(3)))
    print("compose:", compose(f, g, h)(3), "=", f(g(h(3))))
    print("pipe:", pipe(f, g, h)(3), "=", h(g(f(3))))
    original = res1.records[0]
    converted = original
    transformations = [strip_strings, lower_category, to_int_number]
    for transform in transformations:
        converted = transform(converted)
    print("Цикл і normalize збігаються:", converted == normalize(original))
    print("До нормалізації:", original)
    print("Після нормалізації:", converted)
    category_is = make_predicate("category", "eq", "електроніка")
    print("qty >= 5:", keep(converted), "category == електроніка:", category_is(converted))
    first_total, second_total = make_running_total(), make_running_total()
    print("Перший накопичувач:", first_total(5), first_total(3))
    print("Другий накопичувач:", second_total(2), second_total(1))
    selected = list(select_records(lines))
    running_total = make_running_total()
    totals = [running_total(rec["qty"]) for rec in selected]
    groups = pipeline(lines)
    print("Накопичена сума:", totals[-1], "Сума груп:", sum(groups.values()))
    classify = lambda qty: "мало" if qty < 5 else "звичайно" if qty < 20 else "багато"
    print("Класифікація:", [(qty, classify(qty)) for qty in (3, 5, 19, 20)])

    print("\n4. Конвеєр map / filter / reduce")
    print("Відібрані SKU:", [rec["sku"] for rec in selected])
    print("Кількість за категоріями:", groups)
    print("Порожній вхід:", pipeline([]))

    print("\n5. Часткове застосування та каррирування")
    to_km = partial(scale, 1.60934)  # Милі -> кілометри.
    to_miles = partial(scale, 1 / 1.60934)  # Кілометри -> милі.
    print("100 миль у км:", to_km(100), "100 км у милях:", to_miles(100))
    qty_at_least = partial(make_predicate, "qty", "ge")
    partial_keep = qty_at_least(5)
    curried_keep = curry3(make_predicate)("qty")("ge")(5)
    add_three = lambda a, b, c: a + b + c
    print("curry3:", curry3(add_three)(1)(2)(3), "=", add_three(1, 2, 3))
    print("Після одного аргументу маємо функцію:", callable(curry3(add_three)(1)))
    print("Однаковий відбір:", selected == list(select_records(lines, partial_keep))
          == list(select_records(lines, curried_keep)))
    print("Конвеєр із каррируваним предикатом:", pipeline(lines, curried_keep))

    print("\n6. Ліниві обчислення")
    with open(path, encoding="utf-8") as file:
        lazy_groups = aggregate(g_keep(g_normalize(g_parse(file))))
    print("Агрегація з файлу:", lazy_groups, "Збігається:", lazy_groups == groups)
    print("Відібрані записи збігаються:", list(g_keep(g_normalize(g_parse(lines)))) == selected)
    print("Перші 5 записів нескінченного потоку:")
    for rec in islice(record_stream(), 5):
        print(rec)
    print("Перші 5 після нормалізації та відбору:")
    for rec in islice(g_keep(g_normalize(record_stream())), 5):
        print(rec)
    print("take(3, range(10)):", list(take(3, range(10))))
    print("drop(3, range(6)):", list(drop(3, range(6))))
    generator = take(3, range(10))
    print("Перший обхід:", [item for item in generator])
    print("Повторний обхід:", [item for item in generator])

    print("\n7. Калькулятор виразів")
    expressions = [
        ("Нуль", Num(0)),
        ("(2 + 3) * 4", Mul(Add(Num(2), Num(3)), Num(4))),
        ("-((2 + 3) * 4 - 6)", Neg(Sub(Mul(Add(Num(2), Num(3)), Num(4)), Num(6)))),
        ("Сума 1, 2, 3", Sum((Num(1), Num(2), Num(3)))),
        ("Порожня сума", Sum(())),
        ("2 ** 3", Pow(Num(2), 3)),
        ("2 ** 0", Pow(Num(2), 0)),
        ("Від'ємний показник", Pow(Num(2), -1)),
        ("Корінь із 9", Sqrt(Num(9))),
        ("Корінь із -1", Sqrt(Neg(Num(1)))),
        ("8 / 2", Div(Num(8), Num(2))),
        ("Ділення на обчислений нуль", Div(Num(8), Sub(Num(2), Num(2)))),
        ("Невідомий вузол", "невідомо"),
    ]
    for title, expression in expressions:
        try:
            print(f"{title}: {evaluate(expression)}")
        except ValueError as error:
            print(f"{title}: ValueError: {error}")


if __name__ == "__main__":
    main()
