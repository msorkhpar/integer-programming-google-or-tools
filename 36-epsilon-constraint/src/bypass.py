"""Every NPV floor in $1k steps over the top of the range, with and without AUGMECON2's jump."""

import math

from frontier import augmecon, payoff_table
from gridcap import generate
from objectives import build

small = generate("small")
two = build(small)
risk_plan, npv_plan = payoff_table(two.model, two.risk, two.npv)    # first = risk, second = NPV
span = npv_plan.second - risk_plan.second
low, high = 24_200, round(npv_plan.second)                          # the top $60k of the NPV range

def key(p):
    return round(p.second), round(p.first, 3)                       # (NPV, risk), solver noise removed


seen, solves = [], 0
for floor in range(low, high + 1):                                  # every floor, one solve each
    p, slack = augmecon(two.model, two.risk, two.npv, floor, span)
    solves += 1
    if key(p) not in seen:
        seen.append(key(p))
print(f"every floor {low:,}..{high:,}: {solves} solves, {len(seen)} different plans")

jumped, solves, floor = [], 0, low
while floor <= high:
    p, slack = augmecon(two.model, two.risk, two.npv, floor, span)
    solves += 1
    jumped.append(key(p))
    print(f"  floor {floor:,}: NPV {p.second:,.0f}, risk {p.first:,.1f}, slack {abs(slack):.0f} "
          f"-> jump {1 + math.floor(round(slack, 6))} floors")
    floor += 1 + math.floor(round(slack, 6))
print(f"with the jump: {solves} solves, {len(jumped)} plans, the same ones: {jumped == seen}")
print(f"the whole range {round(risk_plan.second):,}..{high:,} holds {high - round(risk_plan.second) + 1:,} floors")
