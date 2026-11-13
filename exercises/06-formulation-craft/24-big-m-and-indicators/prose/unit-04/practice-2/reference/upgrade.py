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
    """The colleague's version: every row of both modes as a big-M row, with M = 100 throughout."""
    big_m = 100
    model.add_linear_constraint(s >= LINE_CREW[0] - big_m * r, name="line_spend_lo")
    model.add_linear_constraint(s <= LINE_CREW[1] + big_m * r, name="line_spend_hi")
    model.add_linear_constraint(g <= GAIN_PER_DOLLAR * s + big_m * r, name="line_gain")
    model.add_linear_constraint(s >= REBUILD[0] - big_m * (1 - r), name="rebuild_spend_lo")
    model.add_linear_constraint(s <= REBUILD[1] + big_m * (1 - r), name="rebuild_spend_hi")
    model.add_linear_constraint(g <= 40 + big_m * (1 - r), name="rebuild_gain")


def add_hull_modes(model: mathopt.Model, s, g, r) -> None:
    """Line crew (r = 0) or rebuild (r = 1), with a copy of s and g per mode, scaled by its switch."""
    line, rebuild = 1 - r, r
    s_line, s_rebuild = model.add_variable(lb=0, name="s_line"), model.add_variable(lb=0, name="s_rebuild")
    g_line, g_rebuild = model.add_variable(lb=0, name="g_line"), model.add_variable(lb=0, name="g_rebuild")
    model.add_linear_constraint(s == s_line + s_rebuild, name="split_spend")
    model.add_linear_constraint(g == g_line + g_rebuild, name="split_gain")
    model.add_linear_constraint(s_line >= LINE_CREW[0] * line, name="line_spend_lo")
    model.add_linear_constraint(s_line <= LINE_CREW[1] * line, name="line_spend_hi")
    model.add_linear_constraint(g_line <= GAIN_PER_DOLLAR * s_line, name="line_gain")
    model.add_linear_constraint(s_rebuild >= REBUILD[0] * rebuild, name="rebuild_spend_lo")
    model.add_linear_constraint(s_rebuild <= REBUILD[1] * rebuild, name="rebuild_spend_hi")
    model.add_linear_constraint(g_rebuild <= 40 * rebuild, name="rebuild_gain")

if __name__ == "__main__":
    model = mathopt.Model()
    s, g, r = mode_variables(model)
    add_hull_modes(model, s, g, r)
    model.maximize(3 * g - s)
    print(mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value())
