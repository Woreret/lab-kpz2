from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Neg:
    x: "Expr"


@dataclass(frozen=True)
class Add:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Sub:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Mul:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Div:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Pow:
    base: "Expr"
    exp: int


@dataclass(frozen=True)
class Sqrt:
    x: "Expr"


@dataclass(frozen=True)
class Sum:
    terms: tuple["Expr", ...]


Expr = Num | Neg | Add | Sub | Mul | Div | Pow | Sqrt | Sum


def evaluate(node: Expr) -> float:
    match node:
        case Num(0):
            return 0.0
        case Num(value):
            return float(value)
        case Neg(x):
            return -evaluate(x)
        case Add(a, b):
            return evaluate(a) + evaluate(b)
        case Sub(a, b):
            return evaluate(a) - evaluate(b)
        case Mul(a, b):
            return evaluate(a) * evaluate(b)
        case Div(a, b):
            match evaluate(b):
                case 0:
                    raise ValueError("ділення на нуль")
                case denominator:
                    return evaluate(a) / denominator
        case Pow(base, exp) if exp >= 0:
            return evaluate(base) ** exp
        case Pow(_, _):
            raise ValueError("від'ємний показник")
        case Sqrt(x):
            match evaluate(x):
                case value if value < 0:
                    raise ValueError("корінь із від'ємного числа")
                case value:
                    return sqrt(value)
        case Sum([]):
            return 0.0
        case Sum([head, *rest]):
            return evaluate(head) + evaluate(Sum(tuple(rest)))
        case _:
            raise ValueError(f"невідомий вузол: {node!r}")
