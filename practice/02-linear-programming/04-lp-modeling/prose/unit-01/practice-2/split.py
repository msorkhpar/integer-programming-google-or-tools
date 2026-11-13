from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

TOL = 1e-6


@dataclass(frozen=True)
class Terminal:
    name: str
    value: float          # value returned per $k spent
    hours_per_k: float    # dock-crew hours per $k of work
    hours: float          # dock-crew hours available
    floor: float = 0      # least it must get, $k (0: no floor)


def split(terminals: list[Terminal], budget: float):
    """Solve the split LP with GLOP. Returns (status, value, amounts, full rows)."""
    # TODO: the model of the statement (variables, rows, objective), a GLOP solve, the status first,
    # then the value, the amounts and the names of the full rows.
    return "NOT_SOLVED", None, None, None

if __name__ == "__main__":
    port = [Terminal("north", 1.2, 2, 400), Terminal("south", 0.9, 1, 300), Terminal("east", 0.7, 4, 800)]
    print(split(port, 600))
