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
    m_cap = s.upper_bound - LINE_CREW[1]
    m_gain = g.upper_bound - GAIN_PER_DOLLAR * s.lower_bound
    m_floor = REBUILD[0] - s.lower_bound
    model.add_linear_constraint(s <= LINE_CREW[1] + m_cap * r, name="line_spend_cap")
    model.add_linear_constraint(g <= GAIN_PER_DOLLAR * s + m_gain * r, name="line_gain")
    model.add_linear_constraint(s >= REBUILD[0] - m_floor * (1 - r), name="rebuild_spend_floor")


if __name__ == "__main__":
    model = mathopt.Model()
    s, g, r = mode_variables(model)
    add_bigm_modes(model, s, g, r)
    model.maximize(3 * g - s)
    print(mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value())
