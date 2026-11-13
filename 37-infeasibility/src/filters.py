"""Lesson 9.1.3: Chinneck's deletion and additive filters over a model's named rows, with any MathOpt solver.

`Oracle` answers one question, "are these rows, with the rest switched off, infeasible?", by
solving a zero-objective copy of the model in which every other row has lost both bounds. The
variables keep their bounds and integrality: those are what makes x a 0/1 decision, not rules a
planner wrote. The oracle counts its solves, which is the cost of a filter.
"""

from __future__ import annotations

import math

from ortools.math_opt.python import mathopt

from lock_model import solve

R = mathopt.TerminationReason


class Oracle:
    def __init__(self, model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS):
        self.work = mathopt.Model.from_model_proto(model.export_model())   # never edit the caller's model
        self.work.objective.clear()                                         # feasibility only
        self.rows = {r.name: r for r in self.work.linear_constraints()}
        self.bounds = {name: (r.lower_bound, r.upper_bound) for name, r in self.rows.items()}
        self.solver = solver
        self.solves = 0

    def infeasible(self, active) -> bool:
        active = set(active)
        for name, row in self.rows.items():
            lower, upper = self.bounds[name] if name in active else (-math.inf, math.inf)
            row.lower_bound, row.upper_bound = lower, upper
        self.solves += 1
        return solve(self.work, self.solver).termination.reason in (R.INFEASIBLE, R.INFEASIBLE_OR_UNBOUNDED)


def deletion_filter(oracle: Oracle, rules: list[str]) -> list[str]:
    """Drop each rule in turn; keep it out if the rest is still infeasible. One solve per rule."""
    kept = list(rules)
    for name in rules:
        trial = [n for n in kept if n != name]
        if oracle.infeasible(trial):
            kept = trial
    return kept


def additive_filter(oracle: Oracle, rules: list[str]) -> list[str]:
    """Add rules one at a time onto the conflict found so far; the rule that tips the set into
    infeasibility belongs to the conflict. Repeat until the conflict alone is infeasible."""
    conflict: list[str] = []
    while not oracle.infeasible(conflict):
        trial = list(conflict)
        for name in rules:
            if name in conflict:
                continue
            trial.append(name)
            if oracle.infeasible(trial):
                conflict.append(name)
                break
        else:
            raise ValueError("the rules are feasible together: there is no conflict to find")
    return conflict
