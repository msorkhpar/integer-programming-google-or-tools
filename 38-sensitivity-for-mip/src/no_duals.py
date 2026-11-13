"""Lesson 9.2.1: MathOpt reports no dual values for the MILP; its LP relaxation has one, and a gap."""

from gridcap import generate
from selection import build, clean, solve_glop, solve_highs

small = generate("small")
B = small.capital_budget                     # $38,390k

milp = build(small, B)
result = solve_highs(milp.model)
print(f"MILP {result.termination.reason.name}  value {result.objective_value():,.0f}  budget {B:,}")
print("has_dual_feasible_solution:", result.has_dual_feasible_solution())
try:
    result.dual_values(milp.budget)
except ValueError as error:
    print("dual_values:", error)

lp = build(small, B, integer=False)          # the LP relaxation: 0 <= x_i <= 1
relaxed = solve_glop(lp.model)
price = relaxed.dual_values(lp.budget)
print(f"LP relaxation  value {relaxed.objective_value():,.1f}  budget price {clean(price)}")
print(f"gap between the two: {relaxed.objective_value() - result.objective_value():,.1f}")
fractional = {pid: clean(relaxed.variable_values(v), 3) for pid, v in lp.x.items()
              if 1e-6 < relaxed.variable_values(v) < 1 - 1e-6}
print("fractional projects in the LP optimum:", fractional)
more = solve_glop(build(small, B + 1, integer=False).model)  # the same relaxation with $1k more budget
print(f"LP relaxation at B + 1: value {more.objective_value():,.4f}, "
      f"up {more.objective_value() - relaxed.objective_value():.4f}")

# An LP's best value is a concave function of its budget: never below the chord between two budgets.
values = {b: round(solve_highs(build(small, b).model).objective_value()) for b in (38370, 38380, 38390)}
chord = (values[38370] + values[38390]) / 2
print("MILP V(B):", values, f"chord at 38,380: {chord:,.1f}",
      "below the chord" if values[38380] < chord else "on or above")
