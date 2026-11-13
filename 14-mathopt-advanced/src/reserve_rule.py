"""An overrun reserve as MathOpt indicator constraints: written, read back, solved, and refused."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, plan, refusal, solve

small = generate("small")
LARGE = 5000            # $k: a project this size or larger needs a reserve in its start year
SHARE = 0.9             # in such a year, spend stays within 90% of the budget

pm = build(small)
base = solve(pm.model, mathopt.SolverType.GSCIP)
print(f"without the rule   NPV {base.objective_value():,.0f}")

reserve = {}
for p in small.projects:
    if p.capex < LARGE:
        continue
    for t in p.starts():
        reserve[p.project_id, t] = pm.model.add_indicator_constraint(
            indicator=pm.x[p.project_id, t],                     # an existing start variable
            implied_constraint=pm.spend[t] <= SHARE * small.budget[t],
            name=f"reserve_{p.project_id}_{t}")
print("indicator constraints:", pm.model.get_num_indicator_constraints())

ic = reserve["P032", 2027]
print(f"{ic.name}: indicator {ic.indicator_variable.name}, activate_on_zero {ic.activate_on_zero},"
      f" bounds [{ic.lower_bound}, {ic.upper_bound}], {len(list(ic.terms()))} terms")

result = solve(pm.model, mathopt.SolverType.GSCIP)
chosen = plan(pm, result.variable_values())
print(f"with the rule      NPV {result.objective_value():,.0f}  ({result.termination.reason.name}, SCIP)")
for p in small.projects:
    if p.capex >= LARGE and p.project_id in chosen:
        t = chosen[p.project_id]
        spent = sum(q.spend(chosen[q.project_id]).get(t, 0) for q in small.projects if q.project_id in chosen)
        print(f"  {p.project_id} starts {t}: spend {spent:,} of {small.budget[t]:,}"
              f" ({spent / small.budget[t]:.1%})")

for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.CP_SAT, mathopt.SolverType.GLOP):
    try:
        solve(pm.model, solver)
    except Exception as error:                    # the real reason is on __context__
        print(f"{solver.name:6} {type(error).__name__} | reason: {refusal(error)}")

try:
    ic.upper_bound = 0.95 * small.budget[2027]
except AttributeError as error:
    print("change a bound:", error)
pm.model.delete_indicator_constraint(ic)          # to change a rule: delete it and add it again
reserve["P032", 2027] = pm.model.add_indicator_constraint(
    indicator=pm.x["P032", 2027], implied_constraint=pm.spend[2027] <= 0.95 * small.budget[2027],
    name="reserve_P032_2027")
print("after delete and re-add:", pm.model.get_num_indicator_constraints(), "indicator constraints,",
      f"P032 2027 bound {reserve['P032', 2027].upper_bound:,.1f}")
