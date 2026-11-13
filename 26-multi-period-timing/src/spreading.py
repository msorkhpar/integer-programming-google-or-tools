"""A project's cost lands in the years it is worked on, not in its start year."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from timing_model import build, schedule

small = generate("small")
p = small.project("P022")
print(p.project_id, "cost profile", p.cost_profile)
for t in p.starts():
    print(f"  start {t}: spends {p.spend(t)}")


def real_spend(plan: dict[str, int]) -> dict[int, int]:
    spend = {y: 0 for y in small.years}
    for pid, t in plan.items():
        for year, amount in small.project(pid).spend(t).items():
            spend[year] += amount
    return spend


params = mathopt.SolveParameters(relative_gap_tolerance=0.0)
for cash_flow in ("lump", "spread"):
    tm = build(small, cash_flow=cash_flow)
    result = mathopt.solve(tm.model, mathopt.SolverType.HIGHS, params=params)
    spend = real_spend(schedule(tm, result))
    over = {y: spend[y] - small.budget[y] for y in small.years if spend[y] > small.budget[y]}
    print(f"{cash_flow:6} model: NPV ${result.objective_value():,.0f}k, real spend over budget in {over or 'no year'}")

# What += does to a MathOpt expression: it builds a new object and rebinds the name.
model = mathopt.Model()
x = model.add_binary_variable(name="x")
total = mathopt.LinearExpression()
alias = total
total += 360 * x
print(f"after +=: total is a {type(total).__name__}, alias is still a {type(alias).__name__}, "
      f"same object: {total is alias}; alias holds {len(alias.terms)} terms, total {len(mathopt.LinearExpression(total).terms)}")
