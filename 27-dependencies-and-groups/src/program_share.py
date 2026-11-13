"""Lesson 6.5.5: a share of the plan's spend, as a linear row on two spend expressions.

GridCap is a fictional utility's portfolio; the shares below are invented for the lesson.
"""

from gridcap import PROGRAMS, generate
from planning_model import build, money, schedule, solve_highs

small = generate("small")


def spend_of(plan, program=None):
    return sum(p.capex * plan.started(p.project_id) for p in small.projects
               if program is None or p.program == program)


def at_least_share(plan, program, share):    # program spend >= share x total spend
    plan.model.add_linear_constraint(spend_of(plan, program) >= share * spend_of(plan), name=f"min_share_{program}")


def at_most_share(plan, program, share):     # program spend <= share x total spend
    plan.model.add_linear_constraint(spend_of(plan, program) <= share * spend_of(plan), name=f"max_share_{program}")


def report(label, rules):
    plan = build(small)
    for rule, program, share in rules:
        rule(plan, program, share)
    result = solve_highs(plan.model)
    starts = schedule(plan, result)
    total = sum(small.project(i).capex for i in starts)
    shares = {g: sum(small.project(i).capex for i in starts if small.project(i).program == g) / total
              for g in PROGRAMS}
    print(f"{label:30} NPV {money(result.objective_value())}  spend {money(total)}  "
          + "  ".join(f"{g} {v:.1%}" for g, v in shares.items()))


report("no share rule", [])
report("vegetation at least 8%", [(at_least_share, "vegetation", 0.08)])
report("transmission at most 50%", [(at_most_share, "transmission", 0.50)])
report("both", [(at_least_share, "vegetation", 0.08), (at_most_share, "transmission", 0.50)])
