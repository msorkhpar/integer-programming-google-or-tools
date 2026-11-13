"""Lesson 2.3.2: every feasible plan is worth at most every feasible price system's bound."""

from budget_lp import build, solve_glop
from certificates import plan_is_feasible, plan_value, price_bound
from gridcap import PROGRAMS, generate

tiny = generate("tiny")
lp = build(tiny)
model = lp.model


def plan_from(spend: dict[tuple[str, int], float]) -> dict[str, float]:
    plan = {var.name: 0.0 for var in model.variables()}
    plan.update({lp.spend[key].name: amount for key, amount in spend.items()})
    return plan


result = solve_glop(model)
plans = {
    "solver's plan": {var.name: result.variable_values(var) for var in model.variables()},
    "floor spread evenly": plan_from({
        ("distribution", 2027): 880, ("vegetation", 2027): 300, ("transmission", 2027): 1120,
        ("distribution", 2028): 2640, ("vegetation", 2028): 300, ("transmission", 2028): 340,
        ("distribution", 2029): 1320, ("vegetation", 2029): 300, ("transmission", 2029): 690}),
    "transmission first": plan_from({
        ("transmission", 2027): 1720, ("vegetation", 2027): 300, ("distribution", 2027): 280,
        ("transmission", 2028): 2980, ("vegetation", 2028): 300,
        ("transmission", 2029): 2010, ("vegetation", 2029): 300}),
}

zero = {row.name: 0.0 for row in model.linear_constraints()}
price_systems = {
    "cash at 0.66": {**zero, **{lp.cash[y].name: 0.66 for y in tiny.years}},
    "cash 0.5, dist. crews 0.16": {**zero, **{lp.cash[y].name: 0.5 for y in tiny.years},
                                   **{lp.crew["distribution", y].name: 0.16 for y in tiny.years}},
    "solver's duals": {row.name: result.dual_values(row) for row in model.linear_constraints()},
    "solver's cash duals only": {**zero, **{lp.cash[y].name: result.dual_values(lp.cash[y]) for y in tiny.years}},
}

for name, plan in plans.items():
    print(f"plan   {name:27} feasible {plan_is_feasible(model, plan)!s:5}  value {plan_value(model, plan):9,.1f}")
for name, prices in price_systems.items():
    b = price_bound(model, prices)
    print(f"prices {name:27} " + ("prove nothing (not dual feasible)" if b is None else f"bound {b:9,.1f}"))
values = [plan_value(model, p) for p in plans.values()]
bounds = [b for b in (price_bound(model, p) for p in price_systems.values()) if b is not None]
print(f"best plan {max(values):,.1f} <= smallest bound {min(bounds):,.1f}: {max(values) <= min(bounds) + 1e-6}")
