from __future__ import annotations


def set_objective_n_args(levels: list[dict]) -> list[dict]:
    """setObjectiveN keyword arguments, one dict per level, for a model with ModelSense = maximize."""
    # TODO: Gurobi's priority order, the weight that encodes the sense, and the tolerances.
    return [{"index": i, "priority": level["priority"], "weight": 1, "abstol": 1e-6, "reltol": 0,
             "name": "objective"} for i, level in enumerate(levels)]


if __name__ == "__main__":
    levels = [{"name": "urgent", "priority": 0, "maximize": True, "abs_tol": None, "rel_tol": 0.02},
              {"name": "overtime", "priority": 1, "maximize": False, "abs_tol": 2.0, "rel_tol": None}]
    for args in set_objective_n_args(levels):
        print(args)
