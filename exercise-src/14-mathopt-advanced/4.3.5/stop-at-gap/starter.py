from __future__ import annotations

from ortools.math_opt.python import mathopt


def stop_at(target: float):
    """A MIP_SOLUTION callback that stops the solve once the relative gap is at most `target`."""

    def callback(data: mathopt.CallbackData) -> mathopt.CallbackResult:
        # TODO: the relative gap from data.mip_stats.
        return mathopt.CallbackResult(terminate=False)

    return callback


if __name__ == "__main__":
    stats = mathopt.MipStats(primal_bound=98.0, dual_bound=100.0)
    print(stop_at(0.03)(mathopt.CallbackData(event=mathopt.Event.MIP_SOLUTION, mip_stats=stats)).terminate)
