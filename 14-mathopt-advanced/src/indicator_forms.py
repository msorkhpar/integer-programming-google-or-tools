"""The ways to write one indicator constraint, what the solver checks, and the linear row HiGHS needs."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, refusal, solve

small = generate("small")
LARGE, SHARE = 5000, 0.9

# Two spellings of the same rule: a bounded expression, or its three parts.
pm = build(small)
x, spend, cap = pm.x["P032", 2027], pm.spend[2027], SHARE * small.budget[2027]
a = pm.model.add_indicator_constraint(indicator=x, implied_constraint=spend <= cap, name="as_row")
b = pm.model.add_indicator_constraint(indicator=x, implied_expr=spend, implied_ub=cap, name="as_parts")
for ic in (a, b):
    print(f"{ic.name:8}  lb {ic.lower_bound}  ub {ic.upper_bound}  on zero {ic.activate_on_zero}")

# Activate on zero: "unless P032 starts in 2027, 2027 spend is at least 5,000" (a ranged row).
c = pm.model.add_indicator_constraint(indicator=x, activate_on_zero=True,
                                      implied_constraint=(5000 <= spend) <= small.budget[2027], name="floor")
print(f"{c.name:8}  lb {c.lower_bound}  ub {c.upper_bound}  on zero {c.activate_on_zero}")
print("read back:", str(c.get_implied_constraint())[:58], "...")
try:
    solve(pm.model, mathopt.SolverType.GSCIP)
except Exception as error:
    print("SCIP, two-sided row:", refusal(error))
pm.model.delete_indicator_constraint(c)
c = pm.model.add_indicator_constraint(indicator=x, activate_on_zero=True,           # one side only
                                      implied_constraint=spend >= 5000, name="floor")
print("SCIP, one-sided row:", solve(pm.model, mathopt.SolverType.GSCIP).termination.reason.name)

# The indicator must be a binary variable when the model is solved.
toy = mathopt.Model(name="toy")
share = toy.add_variable(lb=0, ub=1, name="share")           # continuous, not binary
work = toy.add_variable(lb=0, ub=10, name="work")
toy.add_indicator_constraint(indicator=share, implied_constraint=work <= 3, name="needs_binary")
toy.maximize(work + share)
try:
    solve(toy, mathopt.SolverType.GSCIP)
except Exception as error:
    print("continuous indicator:", refusal(error))

toy = mathopt.Model(name="toy")
on = toy.add_binary_variable(name="on")
work = toy.add_variable(lb=0, ub=10, name="work")
toy.add_indicator_constraint(indicator=on, activate_on_zero=True, implied_constraint=work == 0, name="off_means_0")
toy.maximize(work - on)
try:
    solve(toy, mathopt.SolverType.GSCIP)
except Exception as error:
    print("SCIP, equality row:", refusal(error))
toy.delete_indicator_constraint(toy.get_indicator_constraint(0))
toy.add_indicator_constraint(indicator=on, activate_on_zero=True, implied_constraint=work <= 0, name="off_means_0")
print("SCIP, work <= 0 instead:", solve(toy, mathopt.SolverType.GSCIP).objective_value())

# The same reserve rule as linear rows, for HiGHS. The budget row already caps spend at B_t, so
# M = (1 - SHARE) * B_t is exact (lesson 6.2.1): x = 1 lowers the cap to SHARE * B_t.
results = {}
for form in ("indicator", "linear"):
    pm = build(small)
    for p in small.projects:
        if p.capex < LARGE:
            continue
        for t in p.starts():
            if form == "indicator":
                pm.model.add_indicator_constraint(indicator=pm.x[p.project_id, t],
                                                  implied_constraint=pm.spend[t] <= SHARE * small.budget[t])
            else:
                pm.model.add_linear_constraint(
                    pm.spend[t] <= small.budget[t] - (1 - SHARE) * small.budget[t] * pm.x[p.project_id, t])
    solver = mathopt.SolverType.GSCIP if form == "indicator" else mathopt.SolverType.HIGHS
    results[form] = solve(pm.model, solver)
    print(f"{form:9} rows, {solver.name:5}  NPV {results[form].objective_value():,.0f}")

# A plain row beside an indicator is a different rule: it holds whether the indicator is 0 or 1.
toy = mathopt.Model(name="toy")
on = toy.add_binary_variable(name="on")
load = toy.add_variable(lb=0, ub=400, name="load")
toy.add_indicator_constraint(indicator=on, implied_constraint=load <= 250, name="if_on")
toy.maximize(load + 100 * on)
result = solve(toy, mathopt.SolverType.GSCIP)
print(f"indicator only:          on {result.variable_values(on):.0f}, load {result.variable_values(load):.0f}")
toy.add_linear_constraint(load <= 250, name="always")              # a plain row, no indicator
result = solve(toy, mathopt.SolverType.GSCIP)
print(f"plus plain load <= 250:  on {result.variable_values(on):.0f}, load {result.variable_values(load):.0f}")

# Rebuild an indicator constraint from its parts. A constant in the row is moved into the bounds.
toy = mathopt.Model(name="toy")
z = toy.add_binary_variable(name="z")
v = toy.add_variable(lb=0, ub=10, name="v")
old = toy.add_indicator_constraint(indicator=z, implied_constraint=2 * v + 5 <= 9, name="rule")
print("stored:", old.get_implied_constraint())
parts = dict(indicator=old.indicator_variable, activate_on_zero=old.activate_on_zero, name=old.name,
             implied_expr=mathopt.fast_sum(t.coefficient * t.variable for t in old.terms()),
             implied_lb=old.lower_bound, implied_ub=old.upper_bound)
toy.delete_indicator_constraint(old)
new = toy.add_indicator_constraint(**parts)
print("rebuilt:", new.get_implied_constraint(), "| on zero", new.activate_on_zero, "| name", new.name)
