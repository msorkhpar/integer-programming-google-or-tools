from __future__ import annotations

from ortools.math_opt.python import mathopt

R = mathopt.TerminationReason


def verdict(termination: mathopt.Termination) -> dict:
    """Is there a plan, is the answer settled, and which limit stopped the run?"""
    reason = termination.reason
    has_plan = reason in (R.OPTIMAL, R.FEASIBLE)
    settled = reason in (R.OPTIMAL, R.INFEASIBLE)
    limit = None
    if reason in (R.FEASIBLE, R.NO_SOLUTION_FOUND) and termination.limit is not None:
        limit = termination.limit.name
    return {"has_plan": has_plan, "settled": settled, "limit": limit}


if __name__ == "__main__":
    stopped = mathopt.Termination(reason=R.FEASIBLE, limit=mathopt.Limit.TIME,
                                  objective_bounds=mathopt.ObjectiveBounds(primal_bound=90.0, dual_bound=100.0))
    print(verdict(stopped))
