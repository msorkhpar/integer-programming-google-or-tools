from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def stop_at(target: float):
    """A MIP_SOLUTION callback that stops the solve once the relative gap is at most `target`."""

    def callback(data: mathopt.CallbackData) -> mathopt.CallbackResult:
        stats = data.mip_stats
        if stats.primal_bound == 0 or not math.isfinite(stats.primal_bound):
            return mathopt.CallbackResult(terminate=False)      # no plan yet, or no gap to measure
        gap = abs(stats.dual_bound - stats.primal_bound) / abs(stats.primal_bound)
        return mathopt.CallbackResult(terminate=gap <= target)

    return callback


if __name__ == "__main__":
    stats = mathopt.MipStats(primal_bound=98.0, dual_bound=100.0)
    print(stop_at(0.03)(mathopt.CallbackData(event=mathopt.Event.MIP_SOLUTION, mip_stats=stats)).terminate)
