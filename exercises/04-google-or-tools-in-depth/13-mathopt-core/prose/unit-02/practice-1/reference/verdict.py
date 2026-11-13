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
    reason = result.termination.reason
    limit = result.termination.limit.name if result.termination.limit is not None else None
    if reason == R.OPTIMAL:
        return Verdict("use", result.objective_value(), 0.0, None)
    if reason == R.FEASIBLE:
        gap = abs(result.dual_bound() - result.primal_bound())
        return Verdict("use-with-gap", result.objective_value(), gap, limit)
    if reason == R.NO_SOLUTION_FOUND:
        return Verdict("retry", None, None, limit)
    if reason == R.INFEASIBLE:
        return Verdict("conflict", None, None, None)
    if reason in (R.UNBOUNDED, R.INFEASIBLE_OR_UNBOUNDED):
        return Verdict("model-error", None, None, None)
    return Verdict("solver-error", None, None, None)


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_binary_variable(name="x")
    model.maximize(x)
    print(verdict(mathopt.solve(model, mathopt.SolverType.HIGHS)))
