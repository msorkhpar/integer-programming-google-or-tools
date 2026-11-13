from __future__ import annotations

import math


def gap_report(primal: float, dual: float) -> dict[str, float | None]:
    """The gap between the incumbent's value (primal) and the best bound (dual), three ways.

    "absolute" is |primal - dual|; "relative_highs" divides it by |primal| (HiGHS's convention);
    "relative_scip" divides it by the smaller of |primal| and |dual| (SCIP's). With no plan the
    primal value is infinite and every entry is None; a relative gap whose divisor is 0 is None.
    """
    # TODO: the three gaps, and None where a gap cannot be computed.
    return {"absolute": 0.0, "relative_highs": 0.0, "relative_scip": 0.0}


if __name__ == "__main__":
    print(gap_report(980.0, 1000.0))
