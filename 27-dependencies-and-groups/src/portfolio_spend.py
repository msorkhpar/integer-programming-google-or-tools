"""Lesson 6.5.5: a portfolio's spend bounded from above (the budget) and from below (a floor).

GridCap is a fictional utility's portfolio; the floors below are invented for the lesson.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from planning_model import build, money, solve_highs, status

small = generate("small")


def solve(label, add_rows):
    plan = build(small)
    add_rows(plan)
    result = solve_highs(plan.model)
    if status(result) != "OPTIMAL":
        print(f"{label:22} {status(result)}")
        return
    values = result.variable_values()
    used = {y: mathopt.evaluate_expression(plan.spend[y], values) for y in small.years}
    shares = "  ".join(f"{y} {used[y] / small.budget[y]:.1%}" for y in small.years)
    print(f"{label:22} NPV {money(result.objective_value())}  spend {money(sum(used.values()))}  {shares}")


def nothing(plan):
    pass


def yearly_floor(share):
    def rows(plan):               # spend at least `share` of each year's budget
        for y in small.years:
            plan.model.add_linear_constraint(plan.spend[y] >= share * small.budget[y], name=f"floor_{y}")
    return rows


def plan_floor(share):
    def rows(plan):               # spend at least `share` of the five budgets together
        total = sum(small.budget.values())
        plan.model.add_linear_constraint(sum(plan.spend.values()) >= share * total, name="floor_plan")
    return rows


print(f"budgets {dict(small.budget)}, total {money(sum(small.budget.values()))}")
solve("budget rows only", nothing)
solve("yearly floor 99%", yearly_floor(0.99))
solve("plan floor 99.5%", plan_floor(0.995))
solve("yearly floor 99.5%", yearly_floor(0.995))
solve("yearly floor 100%", yearly_floor(1.0))
