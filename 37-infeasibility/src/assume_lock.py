"""Lesson 9.1.5: CP-SAT assumptions on the Budget Lock scenario, beyond lesson 4.6.2's single conflict.

GridCap is a fictional utility's portfolio. The CP-SAT model is lock_model's, copied row for row
(convert.to_cpsat); every row but "once" holds only when its flag is true. Four questions: what the
solver names, how the order of a deletion filter picks the conflict, a coarse pass over rule
families before the fine one, and the fewest rows to switch off.
"""

from ortools.sat.python import cp_model

from convert import to_cpsat
from gridcap import generate
from lock_model import LOCK, build

small = generate("small")
lm = build(small, LOCK)
RULES = [n for n in lm.rules if not n.startswith("once_")]
solves = 0


def conflict(assumed: list[str]) -> list[str] | None:
    """Solve with the named flags assumed true. None if feasible, else the flags the solver names."""
    global solves
    solves += 1
    model, flags = to_cpsat(lm.model, flagged=RULES)
    model.clear_objective()                           # a feasibility question
    model.add_assumptions([flags[n] for n in assumed])
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1                 # assumptions need a single worker
    if solver.solve(model) != cp_model.INFEASIBLE:
        return None
    name = {flags[n].index: n for n in RULES}
    return [name[i] for i in solver.sufficient_assumptions_for_infeasibility()]


def minimal(order: list[str]) -> list[str]:
    """Deletion filter over the flags in `order`: the earlier a flag comes, the sooner it is dropped."""
    kept = list(order)
    for n in order:
        trial = [k for k in kept if k != n]
        if conflict(trial) is not None:
            kept = trial
    return kept


PLANNERS = ("budget_", "crews_", "floor_", "force_")          # rows planners and finance set at Budget Lock
core = conflict(RULES)
print(f"{len(RULES)} flags assumed; sufficient set: {len(core)} flags, {sorted(core)}")

# Each sufficient set is small here, so listing every conflict is cheap: switch one row off, ask again.
solves = 0
assumed = list(RULES)
while (named := conflict(assumed)) is not None:
    off = next((n for n in named if n.startswith(PLANNERS)), named[0])   # a planners' row if there is one
    print(f"named {sorted(named)} -> switch off {off}")
    assumed.remove(off)
print(f"feasible with {len(RULES) - len(assumed)} rows off ({solves} solves)")

theirs = [n for n in RULES if n.startswith(PLANNERS)]
model_rules = [n for n in RULES if not n.startswith(PLANNERS)]
for label, order in (("planners' rows tested first", theirs + model_rules),
                     ("planners' rows tested last ", model_rules + theirs)):
    solves = 0
    print(f"{label}: {sorted(minimal(order))}  ({solves} solves)")

# Coarse, then fine: a deletion filter over whole families first, then over the rows of the families kept.
family = {n: n.split("_")[0] for n in RULES}                   # budget_2028 -> budget
solves = 0
kept = sorted(set(family.values()))
for f in list(kept):
    if conflict([n for n in RULES if family[n] in kept and family[n] != f]) is not None:
        kept.remove(f)
print(f"families: {sorted(set(family.values()))} -> needed {kept}  ({solves} solves)")
inside = [n for n in RULES if family[n] in kept]
print(f"rows of those families: {len(inside)}; minimal: {sorted(minimal(inside))}  ({solves} solves in all)")

# The fewest rows to switch off: no assumptions, maximize the number of flags left on.
model, flags = to_cpsat(lm.model, flagged=RULES)
model.maximize(sum(flags.values()))
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.solve(model)
print(f"fewest rows off: {len(RULES) - int(solver.objective_value)}, {sorted(n for n, f in flags.items() if not solver.value(f))}")
