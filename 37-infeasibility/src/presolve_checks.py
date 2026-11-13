"""Lesson 9.1.2: five data errors, each caught by a check before the solve; then the Budget Lock scenario.

GridCap is a fictional utility's portfolio. Each error is planted in a copy of GridCap small, the
way a typo or an override would arrive in real input. For each, the program prints what the solver
says and what the checks say.
"""

from dataclasses import replace

from ortools.math_opt.python import mathopt

from checks import run_checks
from gridcap import generate
from lock_model import LOCK, Scenario, build, solve

small = generate("small")


def edit(portfolio, pid: str, **changes):
    """A copy of the portfolio with one project's fields changed."""
    projects = tuple(replace(p, **changes) if p.project_id == pid else p for p in portfolio.projects)
    return replace(portfolio, projects=projects)


planted = [
    ("P017 window typed 2030-2029", edit(small, "P017", latest_start=2029), Scenario()),
    ("P039 first-year cost 11,700", edit(small, "P039", cost_profile=(11700, 880)), Scenario()),
    ("P003 crew-months typed 3", edit(small, "P003", crew_months=3), Scenario()),
    ("P001 and P002 both must-do", edit(edit(small, "P002", must_do=True), "P001", must_do=True), Scenario()),
    ("Plains floor typed 24,100", replace(small, region_floor={**small.region_floor, "Plains": 24100}), Scenario()),
]
for label, portfolio, scenario in planted:
    reason = solve(build(portfolio, scenario).model).termination.reason.name
    print(f"{label:<29} solver: {reason}")
    for problem in run_checks(portfolio, scenario):
        print(f"   {problem.check:<7}{problem.subject:<7}{problem.detail}")

print("base data:", run_checks(small) or "no problem found")
for scenario in (LOCK, replace(LOCK, name="lock, crews restored", crews={})):
    problems = run_checks(small, scenario)
    reason = solve(build(small, scenario).model).termination.reason.name
    print(f"{scenario.name}: solver {reason}; checks: {[(p.check, p.subject) for p in problems] or 'no problem found'}")

# An empty window leaves a must-do row with no variables. fast_sum keeps it a row; sum() does not.
empty = mathopt.Model()
empty.add_linear_constraint(mathopt.fast_sum([]) == 1, name="must_P017")
print("fast_sum([]) == 1 :", solve(empty).termination.reason.name)
try:
    empty.add_linear_constraint(sum([]) == 1, name="must_P017")
except TypeError as error:
    print("sum([]) == 1      : TypeError,", str(error).split(".")[0])
