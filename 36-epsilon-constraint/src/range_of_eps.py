"""The payoff table: the two single-objective plans, and what ε does below, inside and above their range."""

from frontier import epsilon_constraint, payoff_table
from gridcap import generate
from objectives import build

small = generate("small")
two = build(small)

npv_plan, risk_plan = payoff_table(two.model, two.npv, two.risk)
print("payoff table      |   NPV $k | risk removed $k")
print(f"max NPV plan      | {npv_plan.first:8,.0f} | {npv_plan.second:15,.0f}")
print(f"max risk plan     | {risk_plan.first:8,.0f} | {risk_plan.second:15,.0f}")

for floor in (8_000, 10_576, 14_000, 16_086, 16_200):
    p = epsilon_constraint(two.model, two.npv, two.risk, floor)
    shown = "no plan reaches it" if p is None else f"NPV ${p.first:,.0f}k, risk ${p.second:,.0f}k"
    print(f"risk >= {floor:6,}: {shown}")
