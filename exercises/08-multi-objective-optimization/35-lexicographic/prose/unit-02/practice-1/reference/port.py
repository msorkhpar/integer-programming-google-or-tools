from __future__ import annotations


def set_objective_n_args(levels: list[dict]) -> list[dict]:
    """setObjectiveN keyword arguments, one dict per level, for a model with ModelSense = maximize."""
    top = max(level["priority"] for level in levels)
    return [{"index": i,
             "priority": top - level["priority"],            # Gurobi: the highest priority goes first
             "weight": 1 if level["maximize"] else -1,       # one ModelSense: minimize f = maximize -f
             "abstol": level["abs_tol"] or 0.0,              # MathOpt's unset means no loss
             "reltol": level["rel_tol"] or 0.0,
             "name": level["name"]}
            for i, level in enumerate(levels)]


if __name__ == "__main__":
    levels = [{"name": "urgent", "priority": 0, "maximize": True, "abs_tol": None, "rel_tol": 0.02},
              {"name": "overtime", "priority": 1, "maximize": False, "abs_tol": 2.0, "rel_tol": None}]
    for args in set_objective_n_args(levels):
        print(args)
