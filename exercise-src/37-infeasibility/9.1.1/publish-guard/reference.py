from __future__ import annotations

from ortools.math_opt.python import mathopt

R = mathopt.TerminationReason


def next_step(result: mathopt.SolveResult, max_gap: float) -> str:
    """What the scheduling service does with a solve: publish, rerun, conflict, model-bug, separate or escalate."""
    termination = result.termination
    match termination.reason:
        case R.OPTIMAL:
            return "publish"
        case R.FEASIBLE:
            primal = termination.objective_bounds.primal_bound
            dual = termination.objective_bounds.dual_bound
            if primal == 0:
                return "publish" if dual == primal else "rerun"
            gap = abs(dual - primal) / abs(primal)
            return "publish" if gap <= max_gap else "rerun"
        case R.NO_SOLUTION_FOUND:
            return "rerun"
        case R.INFEASIBLE:
            return "conflict"
        case R.UNBOUNDED:
            return "model-bug"
        case R.INFEASIBLE_OR_UNBOUNDED:
            return "separate"
        case _:
            return "escalate"


if __name__ == "__main__":
    done = mathopt.SolveResult(termination=mathopt.Termination(reason=R.OPTIMAL))
    print(next_step(done, 0.01))
