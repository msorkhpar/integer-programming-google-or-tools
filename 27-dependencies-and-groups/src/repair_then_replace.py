"""Lesson 6.5.3: repair now and replace later, allowed only with a gap between them.

GridCap is a fictional utility's portfolio; the two-year gap is invented for the lesson. GridCap
values each option as if it were done alone, so a plan that does both counts both values; a real
model that allows the sequence needs the replacement's value after a repair.
"""

from gridcap import generate
from planning_model import build, groups_of, money, schedule, solve_highs, status

small = generate("small")
REPLACE, REPAIR = "P001", "P002"        # asset A001, alternative group G001
GAP = 2                                 # a repair buys at least two years before a replacement


def other_groups(plan):                 # the alt rows of every group but G001
    for g, members in groups_of(small).items():
        if g != "G001":
            plan.model.add_linear_constraint(sum(plan.started(i) for i in members) <= 1, name=f"alt_{g}")


def exclusive(plan):                    # the generated rule: never both
    plan.model.add_linear_constraint(plan.started(REPLACE) + plan.started(REPAIR) <= 1, name="alt_G001")


def gap_rows(plan):                     # both allowed if the replacement is at least GAP years later
    for t in small.project(REPLACE).starts():
        too_close = [s for s in small.project(REPAIR).starts() if s > t - GAP]
        plan.model.add_linear_constraint(
            plan.x[REPLACE, t] + sum(plan.x[REPAIR, s] for s in too_close) <= 1,
            name=f"gap_{REPLACE}_{t}")


def gap_repair_2027(plan):              # the gap rows, with the repair fixed in 2027 to see what follows
    gap_rows(plan)
    plan.x[REPAIR, 2027].lower_bound = 1


def unrestricted(plan):                 # the mistake: drop the group row and write nothing
    pass


print(f"{REPAIR} repair may start {list(small.project(REPAIR).starts())}, "
      f"{REPLACE} replace may start {list(small.project(REPLACE).starts())}")
for t in small.project(REPLACE).starts():
    print(f"  replace in {t} conflicts with a repair in {[s for s in small.project(REPAIR).starts() if s > t - GAP]}")
for label, rule in [("never both", exclusive), ("gap of 2", gap_rows),
                    ("gap, repair 2027", gap_repair_2027), ("no rule", unrestricted)]:
    plan = build(small, alternatives=False)
    other_groups(plan)
    rule(plan)
    result = solve_highs(plan.model)
    starts = schedule(plan, result)
    print(f"{label:16}  NPV {money(result.objective_value())}  {REPAIR} {starts.get(REPAIR, '-')}  "
          f"{REPLACE} {starts.get(REPLACE, '-')}")


def allows(rule, repair_year: int, replace_year: int) -> str:
    """Fix the two projects' start years and ask whether the rows accept them."""
    plan = build(small, alternatives=False)
    other_groups(plan)
    rule(plan)
    for (i, t), var in plan.x.items():
        if i in (REPAIR, REPLACE):
            var.lower_bound = var.upper_bound = float((i, t) in ((REPAIR, repair_year), (REPLACE, replace_year)))
    return "allowed" if status(solve_highs(plan.model)) == "OPTIMAL" else "refused"


for pair in [(2027, 2029), (2027, 2030), (2028, 2030), (2027, 2028), (2028, 2029), (2028, 2028)]:
    print(f"repair {pair[0]}, replace {pair[1]}: never both {allows(exclusive, *pair)}, "
          f"gap of 2 {allows(gap_rows, *pair)}")
