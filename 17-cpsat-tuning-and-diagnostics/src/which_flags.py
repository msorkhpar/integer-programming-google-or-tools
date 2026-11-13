"""Lesson 4.6.2: which rule flags make a GridCap scenario infeasible.

GridCap is a fictional utility's portfolio. The scenario keeps 60% of every year's budget on the
small portfolio. Every rule group of the plan has a flag (`cpsat_plan.build(flags=True)`); all flags
are assumed, the solver names a sufficient set, and a deletion filter shrinks it to a minimal one.
"""

from ortools.sat.python import cp_model

from cpsat_plan import build
from gridcap import generate

small = generate("small")
SCENARIO = 0.6


def conflict(assumed: list[str]) -> list[str] | None:
    """Solve with the named flags assumed. None if feasible, else the flags the solver names."""
    plan = build(small, budget_scale=SCENARIO, flags=True)
    plan.model.add_assumptions([plan.flags[name] for name in assumed])
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1                # assumptions need a single worker
    status = solver.solve(plan.model)
    if status != cp_model.INFEASIBLE:
        return None
    by_index = {flag.index: name for name, flag in plan.flags.items()}
    return [by_index[i] for i in solver.sufficient_assumptions_for_infeasibility()]


def minimal(core: list[str]) -> list[str]:
    """Deletion filter: drop each flag in turn and keep it out if the rest is still infeasible."""
    kept = list(core)
    for name in list(core):
        trial = [n for n in kept if n != name]
        if conflict(trial) is not None:
            kept = trial
    return kept


rules = list(build(small, flags=True).flags)
print(f"{len(rules)} rule flags, e.g. {rules[0]}, {rules[4]}, {rules[-1]}")
core = conflict(rules)
print(f"sufficient set: {len(core)} of {len(rules)} flags")
small_core = minimal(core)
print("minimal set:", small_core)
for name in small_core:
    print(f"  drop {name:<12} -> {'feasible' if conflict([n for n in rules if n != name]) is None else 'still infeasible'}")
P017 = small.project("P017")
print(f"P017: must-do, costs ${P017.capex:,}k, may start {P017.earliest_start}-{P017.latest_start}; "
      + ", ".join(f"{y} budget ${int(small.budget[y] * SCENARIO):,}k" for y in P017.starts()))
