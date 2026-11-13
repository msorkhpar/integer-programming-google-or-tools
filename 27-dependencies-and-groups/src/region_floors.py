"""Lesson 6.5.5: each region's spend over the plan held above its rate-case floor.

GridCap is a fictional utility's portfolio; its `region_floor` is the least each region must receive
over the plan. Every project's work ends inside the plan, so a funded project spends its whole
capex in the plan's years.
"""

from gridcap import REGIONS, generate
from planning_model import build, groups_of, money, schedule, solve_highs, status

small = generate("small")


def region_spend(plan, region):
    return sum(p.capex * plan.started(p.project_id) for p in small.projects if p.region == region)


def add_floors(plan, floor):
    for r in REGIONS:
        plan.model.add_linear_constraint(region_spend(plan, r) >= floor[r], name=f"floor_{r}")


def most_spendable(portfolio, region) -> int:
    """The most a region can receive: every project, but only the dearest option of each group."""
    alone = sum(p.capex for p in portfolio.projects if p.region == region and not p.alt_group)
    groups = [max(portfolio.project(i).capex for i in members)
              for members in groups_of(portfolio).values() if portfolio.project(members[0]).region == region]
    return alone + sum(groups)


def precheck(portfolio, floor) -> list[str]:
    problems = [f"{r}: floor {money(floor[r])} above the most it can receive, {money(most_spendable(portfolio, r))}"
                for r in REGIONS if floor[r] > most_spendable(portfolio, r)]
    if sum(floor.values()) > sum(portfolio.budget.values()):
        problems.append(f"floors total {money(sum(floor.values()))}, budgets {money(sum(portfolio.budget.values()))}")
    return problems


def report(label, floor):
    plan = build(small)
    if floor is not None:
        add_floors(plan, floor)
    result = solve_highs(plan.model)
    if status(result) != "OPTIMAL":
        print(f"{label:18} {status(result)}")
        return
    starts = schedule(plan, result)
    got = {r: sum(small.project(i).capex for i in starts if small.project(i).region == r) for r in REGIONS}
    print(f"{label:18} NPV {money(result.objective_value())}  "
          + "  ".join(f"{r} {got[r]:,}" for r in REGIONS))


print("floors             " + "  ".join(f"{r} {small.region_floor[r]:,}" for r in REGIONS))
print("most               " + "  ".join(f"{r} {most_spendable(small, r):,}" for r in REGIONS))
report("no floor", None)
report("floors", small.region_floor)
report("Plains floor 8,000", {**small.region_floor, "Plains": 8_000})
tripled = {r: 3 * v for r, v in small.region_floor.items()}
print(f"floors x3 total {money(sum(tripled.values()))}; precheck:", precheck(small, tripled) or "no problem found")
report("floors x3", tripled)
