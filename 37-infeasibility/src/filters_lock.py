"""Lesson 9.1.3: the deletion and additive filters on the Budget Lock scenario, and every conflict in turn.

GridCap is a fictional utility's portfolio. The filters see the scenario's 70 named rows; HiGHS
answers each feasibility question.
"""

from filters import Oracle, additive_filter, deletion_filter
from gridcap import generate
from lock_model import LOCK, build

small = generate("small")
lm = build(small, LOCK)
rules = list(lm.rules)
print(f"{len(rules)} rows, from {rules[0]} to {rules[-1]}")

for label, filter_, order in (("deletion, build order", deletion_filter, rules),
                              ("deletion, reversed   ", deletion_filter, rules[::-1]),
                              ("additive, build order", additive_filter, rules)):
    oracle = Oracle(lm.model)
    conflict = filter_(oracle, order)
    print(f"{label}: {oracle.solves:>3} solves -> {sorted(conflict)}")

# Every conflict, one at a time: find one, switch off one of its rows, look again (Gurobi's workforce2 loop).
oracle = Oracle(lm.model)
active = list(rules)
while oracle.infeasible(active):
    conflict = deletion_filter(oracle, active)
    dropped = next(n for n in conflict if n.startswith(("force_", "budget_", "crews_")))   # a row planners set
    print(f"conflict {sorted(conflict)} -> switch off {dropped}")
    active.remove(dropped)
print(f"feasible once {len(rules) - len(active)} rows are off; {oracle.solves} solves in all")
