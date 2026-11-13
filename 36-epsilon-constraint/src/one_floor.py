"""The planners' question as one ε-constraint solve: the most NPV that removes at least $13,000k of risk."""

from ortools.math_opt.python import mathopt

from frontier import solve
from gridcap import generate
from objectives import build

small = generate("small")
two = build(small)                    # every rule of lesson 6.4.2, no objective yet

floor = 13_000                        # ε: risk removed must be at least this, $k
row = two.model.add_linear_constraint(two.risk >= floor, name="eps_risk")
two.model.maximize(two.npv)
result = solve(two.model)

values = result.variable_values()
npv = mathopt.evaluate_expression(two.npv, values)
risk = mathopt.evaluate_expression(two.risk, values)
print(f"max NPV s.t. risk removed >= ${floor:,}k: {result.termination.reason.name}")
print(f"  NPV ${npv:,.0f}k, risk removed ${risk:,.0f}k, {len(two.plan(values))} projects")
print(f"  the floor's slack: ${risk - floor:,.0f}k of risk above ε")
