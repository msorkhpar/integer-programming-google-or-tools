"""Lesson 6.2.3: OR-Tools' if-then-else with enforcement literals in CP-SAT, and as MathOpt indicators in SCIP.

"If x < 5 then y = 0, else y = 10 - x", with b true exactly when x >= 5. CP-SAT enforces any row,
equalities included. SCIP, through MathOpt, takes an indicator only when its implied row has one
side, so each equality becomes one or two one-sided indicators.
"""
# Adapted from the OR-Tools example channeling_sample_sat.py, https://github.com/google/or-tools/blob/stable/ortools/sat/samples/channeling_sample_sat.py

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from crew_model import quiet_solve


class Collect(cp_model.CpSolverSolutionCallback):
    """Remember every solution as a tuple of values."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables, self.found = variables, []

    def on_solution_callback(self) -> None:
        self.found.append(tuple(self.value(v) for v in self.variables))


def cpsat_table() -> list[tuple[int, int, int]]:
    """Every solution (x, y, b) of the CP-SAT model."""
    model = cp_model.CpModel()
    x = model.new_int_var(0, 10, "x")
    y = model.new_int_var(0, 10, "y")
    b = model.new_bool_var("b")
    model.add(x >= 5).only_enforce_if(b)          # b == (x >= 5)
    model.add(x < 5).only_enforce_if(~b)
    model.add(y == 10 - x).only_enforce_if(b)     # b implies y == 10 - x
    model.add(y == 0).only_enforce_if(~b)         # not b implies y == 0
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    collect = Collect([x, y, b])
    solver.solve(model, collect)
    return sorted(collect.found)


def indicator_model(one_sided: bool):
    model = mathopt.Model(name="if_then_else")
    x = model.add_integer_variable(lb=0, ub=10, name="x")
    y = model.add_integer_variable(lb=0, ub=10, name="y")
    b = model.add_binary_variable(name="b")
    model.add_indicator_constraint(indicator=b, implied_constraint=x >= 5, name="b_on")
    model.add_indicator_constraint(indicator=b, activate_on_zero=True, implied_constraint=x <= 4, name="b_off")
    if not one_sided:                             # the then-branch as the equality CP-SAT takes
        model.add_indicator_constraint(indicator=b, implied_constraint=y == 10 - x, name="then")
        model.add_indicator_constraint(indicator=b, activate_on_zero=True, implied_constraint=y <= 0, name="else")
    else:
        model.add_indicator_constraint(indicator=b, implied_constraint=y <= 10 - x, name="then_le")
        model.add_indicator_constraint(indicator=b, implied_constraint=y >= 10 - x, name="then_ge")
        model.add_indicator_constraint(indicator=b, activate_on_zero=True, implied_constraint=y <= 0, name="else")
    return model, x, y, b


def scip_table() -> list[tuple[int, int, int]]:
    """For each x from 0 to 10, the y and b SCIP finds with the one-sided indicators."""
    rows = []
    for value in range(11):
        model, x, y, b = indicator_model(one_sided=True)
        x.lower_bound = x.upper_bound = value
        result = quiet_solve(model, mathopt.SolverType.GSCIP)
        rows.append(tuple(round(result.variable_values(v)) for v in (x, y, b)))
    return rows


if __name__ == "__main__":
    cpsat = cpsat_table()
    print("CP-SAT, all solutions (x, y, b):", cpsat)
    model, *_ = indicator_model(one_sided=False)
    try:
        quiet_solve(model, mathopt.SolverType.GSCIP)
    except Exception as error:                  # OR-Tools 9.15 keeps the solver's reason in __context__
        print("SCIP, equality rows:", error.__context__)
    scip = scip_table()
    print("SCIP, one-sided rows, x fixed 0 to 10:", scip)
    print("same table:", scip == cpsat)
