from __future__ import annotations

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model


def best_with_cpsat(value: dict[str, int], cost: dict[str, int], budget: int,
                    requires: list[tuple[str, str]], excludes: list[tuple[str, str]]) -> int:
    """The best total value, from CP-SAT with its own logic constraints."""
    # TODO: the model in CP-SAT, solved.
    return 0

def best_with_highs(value: dict[str, int], cost: dict[str, int], budget: int,
                    requires: list[tuple[str, str]], excludes: list[tuple[str, str]]) -> int:
    """The best total value, from HiGHS through MathOpt with linear rows."""
    # TODO: the same model in MathOpt, solved with HiGHS.
    return 0

if __name__ == "__main__":
    value, cost = {"a": 5, "b": 4, "c": 3}, {"a": 4, "b": 3, "c": 2}
    print(best_with_cpsat(value, cost, 6, [("c", "b")], []), best_with_highs(value, cost, 6, [("c", "b")], []))
