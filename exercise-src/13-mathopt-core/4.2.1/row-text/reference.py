from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def terms_text(row: mathopt.LinearConstraint) -> str:
    """The row's terms, sorted by variable name, as '3 x_a - x_b + 2.5 y'."""
    parts = []
    for term in sorted(row.terms(), key=lambda t: t.variable.name):
        size = abs(term.coefficient)
        body = term.variable.name if size == 1 else f"{size:g} {term.variable.name}"
        if not parts:
            parts.append(("-" if term.coefficient < 0 else "") + body)
        else:
            parts.append((" - " if term.coefficient < 0 else " + ") + body)
    return "".join(parts)


def describe(row: mathopt.LinearConstraint) -> str:
    """One line for one row: 'name: terms <= ub', '>= lb', '== value' or 'lb <= terms <= ub'."""
    lb, ub = row.lower_bound, row.upper_bound
    text = terms_text(row)
    if lb == ub:
        body = f"{text} == {lb:g}"
    elif math.isinf(lb):
        body = f"{text} <= {ub:g}"
    elif math.isinf(ub):
        body = f"{text} >= {lb:g}"
    else:
        body = f"{lb:g} <= {text} <= {ub:g}"
    return f"{row.name}: {body}"


def describe_model(model: mathopt.Model) -> list[str]:
    """Every row of the model, in creation order."""
    return [describe(row) for row in model.linear_constraints()]


if __name__ == "__main__":
    model = mathopt.Model(name="buses")
    a, b = model.add_binary_variable(name="x_a"), model.add_binary_variable(name="x_b")
    model.add_linear_constraint(3 * a + 2 * b <= 10, name="budget")
    print("\n".join(describe_model(model)))
