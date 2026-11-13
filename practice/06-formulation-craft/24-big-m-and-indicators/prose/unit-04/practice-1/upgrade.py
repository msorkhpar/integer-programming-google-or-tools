from __future__ import annotations

from ortools.math_opt.python import mathopt

LINE_CREW = (10, 30)      # $k a line-crew upgrade may spend; its capacity gain is at most half the spend
REBUILD = (60, 100)       # $k a rebuild may spend; its gain is at most 40 (the gain variable's bound)
GAIN_PER_DOLLAR = 0.5


def mode_variables(model: mathopt.Model, integer: bool = True):
    """Spend s, capacity gain g, and r = 1 if the feeder is rebuilt, 0 if a line crew upgrades it."""
    s = model.add_variable(lb=LINE_CREW[0], ub=REBUILD[1], name="spend")
    g = model.add_variable(lb=0, ub=40, name="gain")
    r = model.add_variable(lb=0, ub=1, is_integer=integer, name="rebuild")
    return s, g, r


def add_bigm_modes(model: mathopt.Model, s, g, r) -> None:
    """Line crew (r = 0) or rebuild (r = 1), as big-M rows with M from the variables' bounds."""
    # TODO: your rows, with each M derived from the bounds.
    return None

if __name__ == "__main__":
    model = mathopt.Model()
    s, g, r = mode_variables(model)
    add_bigm_modes(model, s, g, r)
    model.maximize(3 * g - s)
    print(mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value())
