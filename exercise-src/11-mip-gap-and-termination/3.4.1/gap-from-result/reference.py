from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def read_gap(result: mathopt.SolveResult) -> dict:
    """The incumbent, the best bound and both gaps of a solve, with None for a number it lacks."""
    bounds = result.termination.objective_bounds
    incumbent = None if math.isinf(bounds.primal_bound) else float(bounds.primal_bound)
    bound = None if math.isinf(bounds.dual_bound) else float(bounds.dual_bound)
    if incumbent is None or bound is None:
        return {"incumbent": incumbent, "bound": bound, "absolute": math.inf, "relative": math.inf}
    absolute = abs(bound - incumbent)
    if absolute == 0:
        relative = 0.0
    elif incumbent == 0:
        relative = math.inf
    else:
        relative = absolute / abs(incumbent)
    return {"incumbent": incumbent, "bound": bound, "absolute": absolute, "relative": relative}


if __name__ == "__main__":
    stopped = mathopt.SolveResult(termination=mathopt.Termination(
        reason=mathopt.TerminationReason.FEASIBLE, limit=mathopt.Limit.TIME,
        objective_bounds=mathopt.ObjectiveBounds(primal_bound=1_000.0, dual_bound=1_040.0)))
    print(read_gap(stopped))
