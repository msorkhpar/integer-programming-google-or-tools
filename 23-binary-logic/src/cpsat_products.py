"""Lesson 6.1.4: CP-SAT writes both products of this lesson as logic, and lists every point they allow.

p = x * y for two Booleans, as a clause and two implications; p = b * x for a Boolean b and an
integer x, as two rows switched by b. Every solution is enumerated, so each table is complete.
"""
# Adapted from the OR-Tools examples boolean_product_sample_sat.py, https://github.com/google/or-tools/blob/stable/ortools/sat/samples/boolean_product_sample_sat.py
# and bool_and_int_var_product_sample_sat.py, https://github.com/google/or-tools/blob/stable/ortools/sat/samples/bool_and_int_var_product_sample_sat.py

from ortools.sat.python import cp_model


class Collect(cp_model.CpSolverSolutionCallback):
    """Remember every solution as a tuple of values."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables, self.found = variables, []

    def on_solution_callback(self) -> None:
        self.found.append(tuple(self.value(v) for v in self.variables))


def enumerate_all(model: cp_model.CpModel, variables) -> list[tuple[int, ...]]:
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    collect = Collect(variables)
    solver.solve(model, collect)
    return sorted(collect.found)


def boolean_product() -> list[tuple[int, ...]]:
    """p = x * y, which is p <=> (x and y): every solution as (x, y, p)."""
    model = cp_model.CpModel()
    x = model.new_bool_var("x")
    y = model.new_bool_var("y")
    p = model.new_bool_var("p")
    model.add_bool_or(~x, ~y, p)        # x and y implies p
    model.add_implication(p, x)         # p implies x
    model.add_implication(p, y)         # p implies y
    return enumerate_all(model, [x, y, p])


def bool_times_int(low: int, high: int) -> list[tuple[int, ...]]:
    """p = b * x for an integer x from low to high: every solution as (b, x, p)."""
    model = cp_model.CpModel()
    b = model.new_bool_var("b")
    x = model.new_int_var(low, high, "x")
    p = model.new_int_var_from_domain(cp_model.Domain(low, high).union_with(cp_model.Domain(0, 0)), "p")
    model.add(p == x).only_enforce_if(b)
    model.add(p == 0).only_enforce_if(~b)
    return enumerate_all(model, [b, x, p])


print("p = x * y, all solutions (x, y, p):", boolean_product())
solutions = bool_times_int(1, 4)
print(f"p = b * x, {len(solutions)} solutions (b, x, p):", solutions)
