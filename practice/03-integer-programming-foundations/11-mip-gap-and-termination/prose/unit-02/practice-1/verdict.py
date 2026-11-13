from __future__ import annotations

from ortools.math_opt.python import mathopt

R = mathopt.TerminationReason


def verdict(termination: mathopt.Termination) -> dict:
    """Is there a plan, is the answer settled, and which limit stopped the run?"""
    # TODO: read termination.reason and termination.limit.
    return {"has_plan": None, "settled": None, "limit": "?"}


if __name__ == "__main__":
    stopped = mathopt.Termination(reason=R.FEASIBLE, limit=mathopt.Limit.TIME,
                                  objective_bounds=mathopt.ObjectiveBounds(primal_bound=90.0, dual_bound=100.0))
    print(verdict(stopped))
