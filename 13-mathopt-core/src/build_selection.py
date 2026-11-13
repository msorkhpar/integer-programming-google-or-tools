"""Build GridCap small's selection model from its formulation, then read the model back."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, plan, solve

small = generate("small")
sel = build(small)
model = sel.model

rows = list(model.linear_constraints())
kinds = {}
for row in rows:
    label = row.name.split("_")[0]
    kinds[label] = kinds.get(label, 0) + 1
print(f"{model.name}: {model.get_num_variables()} variables, {model.get_num_linear_constraints()} rows {kinds}")
x = sel.x["P001"]
print(f"{x.name}: lb={x.lower_bound:g} ub={x.upper_bound:g} integer={x.integer}")

row = sel.budget[2027]
terms = sorted(((t.variable.name, t.coefficient) for t in row.terms()), key=lambda t: -t[1])
print(f"{row.name}: {len(terms)} terms, ub={row.upper_bound:,.0f}; largest: {terms[:3]}")

objective = model.objective
print("maximize:", objective.is_maximize, "| terms:", len(list(objective.linear_terms())),
      "| offset:", objective.offset)

result = solve(model, mathopt.SolverType.HIGHS)
print(result.termination.reason.name, f"NPV {result.objective_value():,.0f}k,", len(plan(sel, result)), "projects funded")
