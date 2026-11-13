from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def read_gap(result: mathopt.SolveResult) -> dict:
    """The incumbent, the best bound and both gaps of a solve, with None for a number it lacks."""
    bounds = result.termination.objective_bounds
    # TODO: turn the two bounds into the four numbers of the report.
    return {"incumbent": None, "bound": None, "absolute": -1.0, "relative": -1.0}


if __name__ == "__main__":
    stopped = mathopt.SolveResult(termination=mathopt.Termination(
        reason=mathopt.TerminationReason.FEASIBLE, limit=mathopt.Limit.TIME,
        objective_bounds=mathopt.ObjectiveBounds(primal_bound=1_000.0, dual_bound=1_040.0)))
    print(read_gap(stopped))
