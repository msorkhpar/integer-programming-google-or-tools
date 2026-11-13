from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def close(x: float, y: float, rel_tol: float) -> bool:
    return math.isclose(x, y, rel_tol=rel_tol, abs_tol=0.0)


def coefficients_match(left: dict, right: dict, rel_tol: float) -> bool:
    if left.keys() != right.keys():
        return False
    return all(close(left[name], right[name], rel_tol) for name in left)


def by_name(model: mathopt.Model) -> tuple[dict, dict, dict]:
    variables, rows, objective = {}, {}, {}
    for v in model.variables():
        variables[v.name] = (v.lower_bound, v.upper_bound, v.integer)
    for row in model.linear_constraints():
        terms = {}
        for term in row.terms():
            terms[term.variable.name] = term.coefficient
        rows[row.name] = (row.lower_bound, row.upper_bound, terms)
    for term in model.objective.linear_terms():
        objective[term.variable.name] = term.coefficient
    return variables, rows, objective


def same_model(a: mathopt.Model, b: mathopt.Model, rel_tol: float = 1e-9) -> bool:
    """True when a and b state the same model, whatever order they were built in.

    Names, bounds, integrality and the objective's sense must match exactly; coefficients and the
    objective's offset may differ by a relative `rel_tol`.
    """
    # TODO: compare by name; exact for names, bounds, integrality and sense; within rel_tol for numbers.
    return False

if __name__ == "__main__":
    first = mathopt.Model(name="first")
    x, y = first.add_binary_variable(name="x"), first.add_binary_variable(name="y")
    first.add_linear_constraint(3 * x + 0.1 * 3 * y <= 4, name="cap")
    second = mathopt.Model(name="second")
    y2, x2 = second.add_binary_variable(name="y"), second.add_binary_variable(name="x")
    second.add_linear_constraint(0.3 * y2 + 3 * x2 <= 4, name="cap")
    print("0.1 * 3 == 0.3:", 0.1 * 3 == 0.3, "| same model:", same_model(first, second))
