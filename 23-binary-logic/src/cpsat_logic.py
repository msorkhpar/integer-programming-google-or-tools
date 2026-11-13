"""Lesson 6.1.2: CP-SAT states an implication in logic, and allows exactly what the linear rows allow.

"If b then x and not y" three ways, as in the OR-Tools sample, and the same rule as two linear rows
in MathOpt: every 0/1 assignment each version allows is listed, in the order b, x, y.
"""
# Adapted from the OR-Tools example reified_sample_sat.py, https://github.com/google/or-tools/blob/stable/ortools/sat/samples/reified_sample_sat.py

from ortools.sat.python import cp_model

from selection_model import allowed_values


class Collect(cp_model.CpSolverSolutionCallback):
    """Remember every solution as a tuple of 0/1 values."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables, self.found = variables, []

    def on_solution_callback(self) -> None:
        self.found.append(tuple(self.value(v) for v in self.variables))


def all_solutions(version: str) -> list[tuple[int, ...]]:
    model = cp_model.CpModel()
    x = model.new_bool_var("x")
    y = model.new_bool_var("y")
    b = model.new_bool_var("b")
    if version == "bool_and":                    # a half-reified bool and
        model.add_bool_and(x, ~y).only_enforce_if(b)
    elif version == "implication":               # two implications
        model.add_implication(b, x)
        model.add_implication(b, ~y)
    elif version == "bool_or":                   # two clauses
        model.add_bool_or(~b, x)
        model.add_bool_or(~b, ~y)
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    collect = Collect([b, x, y])
    solver.solve(model, collect)
    return sorted(collect.found)


def linear_rows(m, v):                           # b <= x and b <= 1 - y
    m.add_linear_constraint(v["b"] <= v["x"])
    m.add_linear_constraint(v["b"] <= 1 - v["y"])


found = {version: all_solutions(version) for version in ("bool_and", "implication", "bool_or")}
found["linear rows"] = allowed_values(linear_rows, ("b", "x", "y"))
print("b -> (x and not y); assignments allowed, as b x y:")
for version, assignments in found.items():
    print(f"  {version:12} {' '.join(''.join(map(str, a)) for a in assignments)}")
print("all four the same:", len({tuple(a) for a in found.values()}) == 1)
