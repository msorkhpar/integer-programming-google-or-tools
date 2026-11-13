"""Lesson 6.5.1: what the must-do projects claim of each year's budget, checked before the solve.

GridCap is a fictional utility's portfolio, generated for this course.
"""

from dataclasses import replace

from gridcap import generate
from planning_model import build, money, schedule, solve_highs, status

small = generate("small")


def least_must_spend(portfolio) -> dict[int, int]:
    """The least the must-dos can spend in each year, whatever start years they get."""
    least = {y: 0 for y in portfolio.years}
    for p in portfolio.projects:
        if p.must_do:
            for y in portfolio.years:
                least[y] += min(p.spend(t).get(y, 0) for t in p.starts())
    return least


def fits_alone(portfolio, p) -> bool:
    """Some start year of `p` keeps its own spend within every year's budget."""
    return any(all(amount <= portfolio.budget[y] for y, amount in p.spend(t).items()) for t in p.starts())


def precheck(portfolio) -> list[str]:
    problems = []
    for p in portfolio.projects:
        if p.must_do and not fits_alone(portfolio, p):
            problems.append(f"{p.project_id} fits the budgets in none of its start years")
    least = least_must_spend(portfolio)
    for y in portfolio.years:
        if least[y] > portfolio.budget[y]:
            problems.append(f"{y}: must-dos need at least {money(least[y])}, budget {money(portfolio.budget[y])}")
    need = sum(p.capex for p in portfolio.projects if p.must_do)
    if need > sum(portfolio.budget.values()):
        problems.append(f"plan: must-dos cost {money(need)}, budgets total {money(sum(portfolio.budget.values()))}")
    return problems


least = least_must_spend(small)
print("year  budget  must-do least  left for discretionary")
for y in small.years:
    print(f"{y}  {small.budget[y]:6,}  {least[y]:13,}  {small.budget[y] - least[y]:22,}")
print("precheck:", precheck(small) or "no problem found")

plan = build(small)
result = solve_highs(plan.model)
starts = schedule(plan, result)
print(f"{status(result)}  NPV {money(result.objective_value())}")
print("year  budget  must-do spend  discretionary spend")
for y in small.years:
    must = sum(small.project(i).spend(t).get(y, 0) for i, t in starts.items() if small.project(i).must_do)
    rest = sum(small.project(i).spend(t).get(y, 0) for i, t in starts.items() if not small.project(i).must_do)
    print(f"{y}  {small.budget[y]:6,}  {must:13,}  {rest:19,}")

for cut in ({2030: 4_000, 2031: 4_000}, {2031: 4_000}, {2030: 5_000, 2031: 5_400}):
    tight = replace(small, budget={**small.budget, **cut})
    print(f"budgets {cut}: precheck {precheck(tight) or 'no problem found'}; "
          f"solve {status(solve_highs(build(tight).model))}")
