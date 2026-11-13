"""Lesson 6.5.1: a must-do as an equality row, and as a large weight in the objective.

GridCap is a fictional utility's portfolio; the budget cut below is invented for the lesson.
"""

from dataclasses import replace

from gridcap import generate
from planning_model import build, money, schedule, solve_highs, status

small = generate("small")
must = [p.project_id for p in small.projects if p.must_do]
BONUS = 100_000          # $k added to a must-do's NPV in the weighted version


def equality(portfolio):
    plan = build(portfolio)                                  # must_i: started(i) == 1
    return plan, 0


def weighted(portfolio):
    plan = build(portfolio, must_do=False)                   # once_i: started(i) <= 1 for every project
    bonus = sum(BONUS * plan.started(i) for i in must)
    plan.model.maximize(plan.model.objective.as_linear_expression() + bonus)
    return plan, bonus


def report(label, portfolio, version):
    plan, _ = version(portfolio)
    result = solve_highs(plan.model)
    if status(result) != "OPTIMAL":
        print(f"  {label:9} {status(result)}")
        return
    starts = schedule(plan, result)
    reported = result.objective_value()
    true_npv = sum(portfolio.project(i).npv[t] for i, t in starts.items())
    funded = [i for i in must if i in starts]
    print(f"  {label:9} {status(result)}  objective {money(reported)}  NPV {money(true_npv)}  "
          f"must-dos funded {len(funded)} of {len(must)}: {funded}")


print("must-do projects:", must)
print("budgets as generated")
report("equality", small, equality)
report("weighted", small, weighted)
cut = replace(small, budget={**small.budget, 2030: 4_000, 2031: 4_000})
print("2030 and 2031 budgets cut to $4,000k")
report("equality", cut, equality)
report("weighted", cut, weighted)
