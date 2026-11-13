"""Lesson 6.1.4: which rows a product z = x_a x_b needs depends on the sign of its objective term.

GridCap is a fictional utility's portfolio. Two invented terms: a $150k bonus for each pair of
same-region distribution projects funded together, and a $400k outage-coordination cost for each
pair of same-region transmission projects funded together. Each is solved with all of z's rows,
with only the rows that push z down, and with only the row that pushes z up.
"""

import itertools

from gridcap import REGIONS, generate
from selection_model import EXACT, build, funded, ids, solve_highs

small = generate("small")


def pairs(program: str) -> list[tuple[str, str]]:
    return [pair for r in REGIONS for pair in itertools.combinations(ids(small, program=program, region=r), 2)]


def plural(n: int) -> str:
    return "pair" if n == 1 else "pairs"


def solve(program: str, amount: int, sides: set[str]):
    sel = build(small)
    model, x = sel.model, sel.x
    z = {}
    for a, b in pairs(program):
        z[a, b] = model.add_binary_variable(name=f"z_{a}_{b}")
        if "down" in sides:
            model.add_linear_constraint(z[a, b] <= x[a])
            model.add_linear_constraint(z[a, b] <= x[b])
        if "up" in sides:
            model.add_linear_constraint(z[a, b] >= x[a] + x[b] - 1)
    model.maximize(model.objective.as_linear_expression() + sum(amount * v for v in z.values()))
    result = solve_highs(model, EXACT)
    plan = set(funded(sel, result))
    real = sum(1 for a, b in z if a in plan and b in plan)
    true_value = sum(small.project(i).value for i in plan) + amount * real
    claimed = sum(1 for v in z.values() if result.variable_values(v) > 0.5)
    return result.objective_value(), true_value, claimed, real


for program, amount, label in (("distribution", 150, "bonus +$150k"), ("transmission", -400, "cost -$400k")):
    print(f"{label} per {program} pair ({len(pairs(program))} pairs)")
    for sides in ({"down", "up"}, {"down"}, {"up"}):
        claimed_value, true_value, claimed, real = solve(program, amount, sides)
        print(f"  rows {'+'.join(sorted(sides)):8} claims ${claimed_value:,.0f}k with {claimed:2} {plural(claimed)}; "
              f"the plan has {real:2} {plural(real)} and is worth ${true_value:,.0f}k")
