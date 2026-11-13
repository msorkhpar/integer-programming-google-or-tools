"""Lesson 7.1.4: GridCap's stakeholder-requirements worksheet, each requirement checked on a real run.

GridCap is a fictional utility's portfolio, generated for this course; the requirements are the
course's examples of what each group asks of a CIPT-style optimizer, not any utility's list.
"""

from gridcap import REGIONS, generate
from cycle_model import base_scenario, optimize, spend_of

small = generate("small")
scenario = base_scenario(small)
run = optimize(scenario)
rerun = optimize(base_scenario(small))
spend = spend_of(small, run.starts)
funded = [small.project(i) for i in run.starts]

# (id, stakeholder, requirement, what in the model or the run meets it, the check)
WORKSHEET = [
    ("R1", "planner", "every must-do project is in the plan", "must_i rows",
     lambda: all(p.project_id in run.starts for p in small.projects if p.must_do)),
    ("R2", "planner", "no project starts outside its window", "x[i,t] only for t in T_i",
     lambda: all(small.project(i).earliest_start <= t <= small.project(i).latest_start for i, t in run.starts.items())),
    ("R3", "planner", "at most one option per alternative group", "alt_g rows",
     lambda: len({p.alt_group for p in funded if p.alt_group}) == sum(1 for p in funded if p.alt_group)),
    ("R4", "finance", "each year's spend is within its budget", "budget_y rows",
     lambda: all(spend[y] <= scenario.budget[y] for y in small.years)),
    ("R5", "finance", "spend by year adds up to the funded capex", "spend report",
     lambda: sum(spend.values()) == sum(p.capex for p in funded)),
    ("R6", "finance", "the NPV reported is proven optimal", "status and gap 0",
     lambda: run.status == "OPTIMAL"),
    ("R7", "regulator", "each region receives its rate-case floor", "floor_r rows",
     lambda: all(sum(p.capex for p in funded if p.region == r) >= scenario.floor[r] for r in REGIONS)),
    ("R8", "regulator", "the same inputs give the same plan", "snapshot + fixed settings",
     lambda: rerun.snapshot == run.snapshot and rerun.starts == run.starts),
    ("R9", "regulator", "every funded child follows its parent", "after_c,t rows",
     lambda: all(run.starts[p.parent] + p.parent_lag <= run.starts[p.project_id] for p in funded if p.parent)),
]

print(f"{'id':3} {'who':9} {'requirement':44} {'met by':26} check")
for rid, who, need, feature, check in WORKSHEET:
    print(f"{rid:3} {who:9} {need:44} {feature:26} {'PASS' if check() else 'FAIL'}")
