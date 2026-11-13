"""Lesson 6.1.4: a binary times a bounded continuous variable, w = x q, as four linear rows.

GridCap is a fictional utility's portfolio. The invented setting: the vegetation contract sets one
clearance width q, between 3 and 6 metres, for every funded vegetation project. A project's cost is
half fixed and half proportional to the width, and its value is proportional to the width; both
equal GridCap's figures at the 4-metre standard width.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection_model import EXACT, build, funded, ids, solve_highs

LOW, HIGH, STANDARD = 3.0, 6.0, 4.0


def product_rows(model, w, x, q, low=LOW, high=HIGH, which=("down", "up")):
    """The rows that make w = x * q when x is binary and low <= q <= high."""
    if "down" in which:
        model.add_linear_constraint(w <= high * x)
        model.add_linear_constraint(w <= q - low * (1 - x))
    if "up" in which:
        model.add_linear_constraint(w >= low * x)
        model.add_linear_constraint(w >= q - high * (1 - x))


def w_range(x_value: int, q_value: float, which) -> str:
    """The least and greatest w the rows allow, with x and q fixed."""
    ends = []
    for sense in ("min", "max"):
        model = mathopt.Model()
        x = model.add_variable(lb=x_value, ub=x_value)
        q = model.add_variable(lb=q_value, ub=q_value)
        w = model.add_variable(lb=0, ub=HIGH)
        product_rows(model, w, x, q, which=which)
        model.minimize(w) if sense == "min" else model.maximize(w)
        ends.append(solve_highs(model).objective_value())
    return f"{ends[0]:.1f}" if ends[0] == ends[1] else f"{ends[0]:.1f} to {ends[1]:.1f}"


def width_model(portfolio, *, integer: bool = True, high_in_rows: float = HIGH, fixed: float | None = None):
    """GridCap's selection model with one clearance width for the vegetation program."""
    sel = build(portfolio, integer=integer)
    model, x = sel.model, sel.x
    vegetation = ids(portfolio, program="vegetation")
    q = model.add_variable(lb=LOW, ub=HIGH, name="q")
    if fixed is not None:
        q.lower_bound = q.upper_bound = fixed
    w = {i: model.add_variable(lb=0, ub=high_in_rows, name=f"w_{i}") for i in vegetation}
    for i in vegetation:
        product_rows(model, w[i], x[i], q, high=high_in_rows)
        p = portfolio.project(i)
        sel.budget.set_coefficient(x[i], p.capex / 2)                 # fixed half of the cost
        sel.budget.set_coefficient(w[i], p.capex / 2 / STANDARD)      # cost per metre of width
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects if p.project_id not in w)
                   + sum(portfolio.project(i).value / STANDARD * w[i] for i in vegetation))
    return sel, q, w


if __name__ == "__main__":
    print("x  q   | x*q | four rows | 'down' rows only | 'up' rows only")
    for x_value in (0, 1):
        for q_value in (3.0, 4.5, 6.0):
            print(f"{x_value}  {q_value:<3} | {x_value * q_value:3.1f} | {w_range(x_value, q_value, ('down', 'up')):9} | "
                  f"{w_range(x_value, q_value, ('down',)):16} | {w_range(x_value, q_value, ('up',))}")

    small = generate("small")
    print("GridCap small, one clearance width for every funded vegetation project")
    for fixed in (3.0, 4.0, 5.0, 6.0, None):
        sel, q, w = width_model(small, fixed=fixed)
        result = solve_highs(sel.model, EXACT)
        veg = [i for i in funded(sel, result) if i in w]
        label = f"q fixed at {fixed:.0f}" if fixed else "q chosen   "
        print(f"  {label}: q = {result.variable_values(q):.3f}, NPV ${result.objective_value():,.1f}k, "
              f"{len(veg)} vegetation projects")
