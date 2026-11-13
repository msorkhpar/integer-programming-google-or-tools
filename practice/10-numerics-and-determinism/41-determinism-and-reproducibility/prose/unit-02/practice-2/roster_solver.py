from __future__ import annotations

from ortools.sat.python import cp_model


def configure(solver: cp_model.CpSolver, seed: int, workers: int, work: float) -> cp_model.CpSolver:
    """Set the solver up so that a run with these numbers repeats."""
    # TODO: write it.
    return solver


if __name__ == "__main__":
    print(configure(cp_model.CpSolver(), seed=11, workers=4, work=5.0).parameters)
