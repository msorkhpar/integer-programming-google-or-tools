"""Rewrite the program-split LP in standard form, max c.x s.t. A x <= b, x >= 0, and solve that."""

import math

import numpy as np
from ortools.math_opt.python import mathopt

from program_split import build


def to_standard_form(model: mathopt.Model):
    """(c, A, b, row labels, variables) with every row a <=, every variable >= 0, and max."""
    variables = list(model.variables())
    column = {v: j for j, v in enumerate(variables)}
    assert all(v.lower_bound == 0 for v in variables), "a variable with another lower bound needs a shift"
    rows, b, labels = [], [], []

    def add(coefficients: dict, rhs: float, label: str) -> None:
        row = np.zeros(len(variables))
        for v, a in coefficients.items():
            row[column[v]] = a
        rows.append(row), b.append(rhs), labels.append(label)

    for con in model.linear_constraints():
        a = {t.variable: t.coefficient for t in con.terms()}
        if math.isfinite(con.upper_bound):                       # a.x <= ub stays as it is
            add(a, con.upper_bound, con.name)
        if math.isfinite(con.lower_bound):                       # a.x >= lb  becomes  -a.x <= -lb
            add({v: -c for v, c in a.items()}, -con.lower_bound, f"{con.name} (x -1)")
    for v in variables:
        if math.isfinite(v.upper_bound):                         # an upper bound is one more row
            add({v: 1.0}, v.upper_bound, f"{v.name} <= ub")
    sign = 1.0 if model.objective.is_maximize else -1.0          # min f  is  max -f
    c = np.zeros(len(variables))
    for term in model.objective.linear_terms():
        c[column[term.variable]] = sign * term.coefficient
    return c, np.array(rows), np.array(b), labels, variables


def solve_matrix(c, A, b) -> float:
    """Build a fresh model straight from the matrices: max c.x, A x <= b, x >= 0."""
    model = mathopt.Model(name="standard form")
    x = [model.add_variable(lb=0, name=f"x{j}") for j in range(len(c))]
    for i in range(len(b)):
        model.add_linear_constraint(sum(A[i, j] * x[j] for j in range(len(c)) if A[i, j]) <= b[i], name=f"r{i}")
    model.maximize(sum(c[j] * x[j] for j in range(len(c))))
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


if __name__ == "__main__":
    split = build(2027)
    c, A, b, labels, variables = to_standard_form(split.model)
    print(f"{'row':26}" + "".join(f"{v.name:>17}" for v in variables) + f"{'b':>10}")
    for label, row, rhs in zip(labels, A, b):
        print(f"{label:26}" + "".join(f"{a:17.5g}" for a in row) + f"{rhs:10,.1f}")
    print(f"{'c (max)':26}" + "".join(f"{a:17.5g}" for a in c))
    original = mathopt.solve(split.model, mathopt.SolverType.GLOP).objective_value()
    print(f"original model NPV {original:,.1f}   standard form NPV {solve_matrix(c, A, b):,.1f}")
