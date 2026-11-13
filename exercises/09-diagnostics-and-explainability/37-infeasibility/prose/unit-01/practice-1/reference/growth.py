from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def free_to_grow(model: mathopt.Model) -> list[str]:
    """Names of the variables the objective pushes in a direction that no bound and no row limits."""
    sense = 1.0 if model.objective.is_maximize else -1.0
    limited_up, limited_down = set(), set()
    for row in model.linear_constraints():
        has_upper, has_lower = not math.isinf(row.upper_bound), not math.isinf(row.lower_bound)
        for term in row.terms():
            if term.coefficient > 0:
                if has_upper:
                    limited_up.add(term.variable)
                if has_lower:
                    limited_down.add(term.variable)
            elif term.coefficient < 0:
                if has_lower:
                    limited_up.add(term.variable)
                if has_upper:
                    limited_down.add(term.variable)
    found = []
    for v in model.variables():
        push = sense * model.objective.get_linear_coefficient(v)
        if push > 0 and math.isinf(v.upper_bound) and v not in limited_up:
            found.append(v.name)
        elif push < 0 and math.isinf(v.lower_bound) and v not in limited_down:
            found.append(v.name)
    return sorted(found)


if __name__ == "__main__":
    model = mathopt.Model()
    order = model.add_variable(lb=0, name="order_gloves")
    refund = model.add_variable(lb=0, name="supplier_refund")
    model.add_linear_constraint(order <= 500, name="storage")
    model.maximize(2 * refund - order)
    print(free_to_grow(model))
