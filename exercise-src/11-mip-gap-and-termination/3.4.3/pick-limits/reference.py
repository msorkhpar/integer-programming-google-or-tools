from __future__ import annotations

import datetime

from ortools.math_opt.python import mathopt


def limits_for(request: dict) -> mathopt.SolveParameters:
    """A planner's stopping request, in dollars, percent and minutes, as MathOpt parameters (objective in $k)."""
    params = mathopt.SolveParameters()
    if request["matters_dollars"] is not None:
        params.absolute_gap_tolerance = request["matters_dollars"] / 1000
    share = request["share_percent"]
    params.relative_gap_tolerance = share / 100 if share is not None else 0.0
    if request["nodes"] is not None:
        params.node_limit = request["nodes"]
    elif request["minutes"] is not None:
        params.time_limit = datetime.timedelta(minutes=request["minutes"])
    return params


if __name__ == "__main__":
    print(limits_for({"matters_dollars": 50_000, "share_percent": 0.5, "minutes": 30, "nodes": None}))
