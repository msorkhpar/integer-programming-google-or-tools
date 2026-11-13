from __future__ import annotations

from ortools.sat.python import cp_model


def outcome(status: int, objective: float, bound: float, limit_s: float) -> dict:
    """Map a CP-SAT status of a maximization solve to the job service's status, value, gap and message.

    `objective` and `bound` are `solver.objective_value` and `solver.best_objective_bound`; the
    service sets only a time limit, so a FEASIBLE or UNKNOWN status means that limit stopped it.
    """
    if status == cp_model.OPTIMAL:
        return {"status": "optimal", "value": objective, "gap": 0.0,
                "message": f"Best roster found and proven: value {objective:g}."}
    if status == cp_model.FEASIBLE:
        gap = max(0.0, bound - objective) / max(abs(objective), 1.0)
        return {"status": "time_limit", "value": objective, "gap": gap,
                "message": f"Stopped at the {limit_s:g} s limit with a roster worth {objective:g}; "
                           f"none is worth more than {bound:g}."}
    if status == cp_model.UNKNOWN:
        return {"status": "time_limit", "value": None, "gap": None,
                "message": f"No roster found within the {limit_s:g} s limit; that does not mean none exists."}
    if status == cp_model.INFEASIBLE:
        return {"status": "infeasible", "value": None, "gap": None,
                "message": "No roster meets every rule."}
    return {"status": "failed", "value": None, "gap": None,
            "message": "The solver refused the model; the request was not judged."}


if __name__ == "__main__":
    print(outcome(cp_model.FEASIBLE, 80.0, 100.0, 30))
