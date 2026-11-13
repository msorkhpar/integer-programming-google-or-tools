"""Lesson 9.2.2: fix the MILP's integers, re-solve the LP that is left, and read what its prices mean.

The selection model with routine line clearance, a continuous variable (selection.py). GridCap is
fictional, and the clearance program's return and cap are this module's assumptions.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import CLEARANCE_RATE, build, clean, funded, row, slack, solve_highs

small = generate("small")


def fix_integers(sel, result) -> None:
    """Fix every integer variable at its value in `result`, and make it continuous."""
    for v in sel.x.values():
        value = round(result.variable_values(v))
        v.integer = False
        v.lower_bound = value
        v.upper_bound = value


def fixed_lp(budget: int):
    """Solve the MILP at `budget`, then fix its plan and re-solve the LP that is left (GLOP)."""
    sel = build(small, budget, clearance=True)
    milp = solve_highs(sel.model)
    fix_integers(sel, milp)
    return sel, milp, mathopt.solve(sel.model, mathopt.SolverType.GLOP)


def milp_value(budget: int) -> float:
    return solve_highs(build(small, budget, clearance=True).model).objective_value()


if __name__ == "__main__":
    B = small.capital_budget
    sel, milp, lp = fixed_lp(B)
    y = milp.variable_values(sel.clearance)
    print(f"MILP at {B:,}: value {milp.objective_value():,.1f}, {len(funded(sel, milp))} projects, clearance {y:,.0f}")
    print(f"fixed LP: {lp.termination.reason.name}, value {lp.objective_value():,.1f}, "
          f"duals: {lp.has_dual_feasible_solution()}")
    for c in (sel.budget, sel.clearance_cap, row(sel.model, "must_P003")):
        print(f"  {c.name:14} slack {clean(slack(c, lp), 1):>6}  dual {clean(lp.dual_values(c))}")
    for pid in ("P003", "P034", "P006", "P001"):
        p = small.project(pid)
        print(f"  x_{pid} = {lp.variable_values(sel.x[pid]):g}  reduced cost {clean(lp.reduced_costs(sel.x[pid]), 1):>6}"
              f"  (value {p.value} - {CLEARANCE_RATE} x capex {p.capex} = {p.value - CLEARANCE_RATE * p.capex:g})")

    # The price as a forecast: the fixed plan at B + d, the MILP at B + d, and price x d.
    price = lp.dual_values(sel.budget)
    print(f"\nbudget {B:,}, clearance {y:,.0f} of 800: with the plan fixed the price holds for d in [{-y + 0.0:,.0f}, {800 - y:,.0f}]")
    print(f"{'d':>6} {'price x d':>9} {'fixed plan':>10} {'MILP':>8}")
    for d in (-100, -10, 10, 100, 500, 800, 1000):
        sel.budget.upper_bound = B + d
        again = mathopt.solve(sel.model, mathopt.SolverType.GLOP)
        fixed_gain = (f"{again.objective_value() - milp.objective_value():,.1f}"
                      if again.termination.reason == mathopt.TerminationReason.OPTIMAL else "infeasible")
        print(f"{d:>+6} {price * d:>9,.1f} {fixed_gain:>10} {milp_value(B + d) - milp.objective_value():>8,.1f}")

    for budget in (38000, 66000):
        sel, milp, lp = fixed_lp(budget)
        y = milp.variable_values(sel.clearance)
        print(f"\nbudget {budget:,}: clearance {y:,.0f}, budget slack {clean(slack(sel.budget, lp), 1):,}, "
              f"budget dual {clean(lp.dual_values(sel.budget))}, cap dual {clean(lp.dual_values(sel.clearance_cap))}")
        print("  MILP gain for d = -100, +10, +100, +1000:",
              [round(milp_value(budget + d) - milp.objective_value(), 1) for d in (-100, 10, 100, 1000)])

    # A row by its name: MathOpt's Model looks rows up by id only, so selection.row walks the rows.
    print("\nModel has get_linear_constraint_by_name:", hasattr(mathopt.Model, "get_linear_constraint_by_name"))
    budget_row = row(sel.model, "budget")
    print(f"row(model, 'budget'): {budget_row.name}, id {budget_row.id}; "
          f"get_linear_constraint({budget_row.id}): {sel.model.get_linear_constraint(budget_row.id).name}")
