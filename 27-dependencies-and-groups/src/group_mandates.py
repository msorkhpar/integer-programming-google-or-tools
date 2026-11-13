"""Lesson 6.5.1: mandates on a group of projects rather than on one project.

GridCap is a fictional utility's portfolio; the two mandates below are invented for the lesson.
"""

from gridcap import generate
from planning_model import build, groups_of, money, schedule, solve_highs, status

small = generate("small")
groups = groups_of(small)                     # {'G001': ['P001', 'P002'], 'G030': ['P030', 'P031']}
UNDERGROUND = ["P024", "P037"]                # the two Ridge undergrounding projects


def nothing(plan):
    pass


def address_each_asset(plan):     # every asset with an alternative group is repaired or replaced
    for g, members in groups.items():
        plan.model.add_linear_constraint(sum(plan.started(i) for i in members) == 1, name=f"address_{g}")


def underground_one(plan):        # at least one Ridge circuit is put underground in the plan
    plan.model.add_linear_constraint(sum(plan.started(i) for i in UNDERGROUND) >= 1, name="underground_Ridge")


def underground_both(plan):       # the mistake: each member of the group made a must-do
    for i in UNDERGROUND:
        plan.model.add_linear_constraint(plan.started(i) == 1, name=f"must_{i}")


def address_both(plan):           # the same mistake on an alternative group
    for i in groups["G030"]:
        plan.model.add_linear_constraint(plan.started(i) == 1, name=f"must_{i}")


base = None
for label, rows in [("no group mandate", nothing), ("address each asset", address_each_asset),
                    ("underground one", underground_one), ("underground both", underground_both),
                    ("both G030 members", address_both)]:
    plan = build(small)
    rows(plan)
    result = solve_highs(plan.model)
    if status(result) != "OPTIMAL":
        print(f"{label:18}  {status(result)}")
        continue
    starts = schedule(plan, result)
    npv = result.objective_value()
    base = npv if base is None else base
    picked = {i: starts.get(i, "-") for i in [*groups["G001"], *groups["G030"], *UNDERGROUND]}
    print(f"{label:18}  NPV {money(npv)}  costs {money(base - npv):>7}  starts {picked}")
