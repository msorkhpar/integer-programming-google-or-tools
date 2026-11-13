from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

R = mathopt.TerminationReason


@dataclass(frozen=True)
class Verdict:
    action: str                 # use, use-with-gap, retry, conflict, model-error, solver-error
    value: float | None         # the plan's objective value, when the plan may be used
    gap: float | None           # |dual bound - primal bound| when a plan may be used
    limit: str | None           # the limit's name, when a limit stopped the solve


def verdict(result: mathopt.SolveResult) -> Verdict:
    """What the caller should do with this result."""
    # TODO: one branch per row of the table in the statement.
    return Verdict("unknown", None, None, None)


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_binary_variable(name="x")
    model.maximize(x)
    print(verdict(mathopt.solve(model, mathopt.SolverType.HIGHS)))
