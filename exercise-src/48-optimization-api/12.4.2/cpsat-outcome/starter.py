from __future__ import annotations

from ortools.sat.python import cp_model  # noqa: F401


def outcome(status: int, objective: float, bound: float, limit_s: float) -> dict:
    """Map a CP-SAT status of a maximization solve to the job service's status, value, gap and message.

    `objective` and `bound` are `solver.objective_value` and `solver.best_objective_bound`; the
    service sets only a time limit, so a FEASIBLE or UNKNOWN status means that limit stopped it.
    """
    # TODO: one branch per CP-SAT status: OPTIMAL, FEASIBLE, UNKNOWN, INFEASIBLE, MODEL_INVALID.
    return {"status": "pending", "value": None, "gap": None, "message": ""}


if __name__ == "__main__":
    print(outcome(cp_model.FEASIBLE, 80.0, 100.0, 30))
