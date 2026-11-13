from __future__ import annotations

from ortools.math_opt.python import mathopt

R = mathopt.TerminationReason


def next_step(result: mathopt.SolveResult, max_gap: float) -> str:
    """What the scheduling service does with a solve: publish, rerun, conflict, model-bug, separate or escalate."""
    # TODO: one case per termination reason, and the gap rule for a plan stopped by a limit.
    return "publish"


if __name__ == "__main__":
    done = mathopt.SolveResult(termination=mathopt.Termination(reason=R.OPTIMAL))
    print(next_step(done, 0.01))
