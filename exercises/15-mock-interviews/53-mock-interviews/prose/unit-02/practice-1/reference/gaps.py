from __future__ import annotations

import math


def gap_report(primal: float, dual: float) -> dict[str, float | None]:
    """The gap between the incumbent's value (primal) and the best bound (dual), three ways.

    "absolute" is |primal - dual|; "relative_highs" divides it by |primal| (HiGHS's convention);
    "relative_scip" divides it by the smaller of |primal| and |dual| (SCIP's). With no plan the
    primal value is infinite and every entry is None; a relative gap whose divisor is 0 is None.
    """
    if math.isinf(primal):
        return {"absolute": None, "relative_highs": None, "relative_scip": None}
    absolute = abs(primal - dual)
    by_incumbent = abs(primal)
    by_smaller = min(abs(primal), abs(dual))
    return {
        "absolute": absolute,
        "relative_highs": absolute / by_incumbent if by_incumbent > 0 else None,
        "relative_scip": absolute / by_smaller if by_smaller > 0 else None,
    }


if __name__ == "__main__":
    print(gap_report(980.0, 1000.0))
