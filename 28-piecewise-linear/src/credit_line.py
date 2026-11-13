"""Lesson 6.6.1: a tiered borrowing cost in GridCap's selection model, written without binaries.

GridCap is a fictional utility's portfolio, and the credit line is invented for this lesson. The
treasury lets the plan spend past the capital budget by drawing on a credit line; each tier of the
line has a cost per $k drawn (the present value of its interest and fees, in $k). The program
solves the model with rising tiers, written as segments and as lines, then with falling tiers.
"""

from gridcap import generate
from piecewise import Curve, add_epigraph, add_segments, value
from selection import EXACT, build, funded, solve_highs


def tiers(widths, rates) -> Curve:
    """Total cost against amount drawn, from each tier's width ($k) and cost per $k drawn."""
    xs, ys = [0.0], [0.0]
    for width, rate in zip(widths, rates):
        xs.append(xs[-1] + width)
        ys.append(ys[-1] + rate * width)
    return Curve(tuple(xs), tuple(ys))


RISING = tiers((1500, 1500, 2000), (0.10, 0.25, 0.45))
FALLING = tiers((1500, 1500, 2000), (0.45, 0.25, 0.10))


def with_credit(portfolio, curve, form):
    """The selection model with a credit line: spend may exceed the budget by what is drawn, at its cost."""
    sel = build(portfolio)
    model = sel.model
    loan = form(model, curve, "loan")
    model.delete_linear_constraint(sel.budget)
    spend = sum(p.capex * sel.x[p.project_id] for p in portfolio.projects)
    model.add_linear_constraint(spend <= portfolio.capital_budget + loan.x, name="budget")
    model.maximize(sum(p.value * sel.x[p.project_id] for p in portfolio.projects) - loan.y)
    return sel, loan


def report(label, portfolio, curve, form):
    sel, loan = with_credit(portfolio, curve, form)
    result = solve_highs(sel.model, EXACT)
    drawn = value(result, loan.x)
    npv = sum(portfolio.project(i).value for i in funded(sel, result))
    print(f"{label}: objective ${result.objective_value():,.0f}k, {len(funded(sel, result))} projects, "
          f"drawn ${drawn:,.0f}k")
    if loan.parts:
        print("    tiers used ($k):", [round(result.variable_values(d)) for d in loan.parts["delta"]])
    print(f"    cost charged by the model ${npv - result.objective_value():,.0f}k, "
          f"real cost ${curve(drawn):,.0f}k, plan really worth ${npv - curve(drawn):,.0f}k")
    integer = sum(v.integer for v in sel.model.variables())
    print(f"    {integer} integer variables, {sel.model.get_num_variables() - integer} continuous")


if __name__ == "__main__":
    small = generate("small")
    base = build(small)
    result = solve_highs(base.model, EXACT)
    print(f"no credit line: objective ${result.objective_value():,.0f}k, {len(funded(base, result))} projects")
    print("rising tiers, slopes", RISING.slopes())
    report("rising, as segments", small, RISING, add_segments)
    report("rising, as lines   ", small, RISING, add_epigraph)
    print("falling tiers, slopes", FALLING.slopes())
    report("falling, as segments", small, FALLING, add_segments)
