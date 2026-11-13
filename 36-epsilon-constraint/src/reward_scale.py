"""Why AUGMECON's slack reward is tiny and divided by the range: a reward of 1 per $k of slack trades NPV away."""

from ortools.math_opt.python import mathopt

from frontier import augmecon, payoff_table, score, solve
from gridcap import generate
from objectives import build

small = generate("small")
two = build(small)
a, b = payoff_table(two.model, two.npv, two.risk)
span = b.second - a.second
floor = 13_000

p, slack = augmecon(two.model, two.npv, two.risk, floor, span)            # reward rho/span = 1e-3/span
print(f"reward 1e-3/{span:,.0f} per $k of slack: NPV ${p.first:,.0f}k, risk ${p.second:,.0f}k, slack {slack:,.0f}")

s = two.model.add_variable(lb=0.0, name="eps_slack")                       # the same rows, reward 1 per $k
row = two.model.add_linear_constraint(two.risk - s == floor, name="eps_floor")
two.model.maximize(two.npv + 1.0 * s)
result = solve(two.model)
q = score(two.npv, two.risk, result.variable_values())
print(f"reward 1 per $k of slack:       NPV ${q.first:,.0f}k, risk ${q.second:,.0f}k, "
      f"slack {result.variable_values(s):,.0f}")
print(f"the big reward gave up ${p.first - q.first:,.0f}k of NPV for ${q.second - p.second:,.0f}k more risk")
