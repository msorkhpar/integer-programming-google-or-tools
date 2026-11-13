from __future__ import annotations

import datetime

from ortools.math_opt.python import mathopt


def limits_for(request: dict) -> mathopt.SolveParameters:
    """A planner's stopping request, in dollars, percent and minutes, as MathOpt parameters (objective in $k)."""
    params = mathopt.SolveParameters()
    # TODO: convert each part of the request into its SolveParameters field.
    params.relative_gap_tolerance = -1.0
    return params


if __name__ == "__main__":
    print(limits_for({"matters_dollars": 50_000, "share_percent": 0.5, "minutes": 30, "nodes": None}))
