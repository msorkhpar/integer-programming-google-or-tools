"""Why a season has no plan: the planner's rules that cannot all hold together, in the planner's words.

Every rule a planner can change (a must, the budget, an override) sits behind a literal (model.py). The
search takes those literals as assumptions; when it proves the season infeasible, CP-SAT names a set of
assumptions that is enough for the proof, and a deletion filter shrinks it to a minimal one: drop each
rule in turn, and keep it out only if the rest still cannot hold.
"""

from __future__ import annotations

from ortools.sat.python import cp_model

from vegcrew.data import Override, Season
from vegcrew.model import TrimModel, build


def holds(tm: TrimModel, names: list[str]) -> bool:
    """Can these rules all hold at once? One worker, stopped at the first plan: only yes or no matters."""
    tm.model.clear_assumptions()
    tm.model.add_assumptions([tm.rules[n] for n in names])
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.stop_after_first_solution = True
    return solver.solve(tm.model) != cp_model.INFEASIBLE


def conflict(tm: TrimModel) -> list[str]:
    """A minimal set of rule names that cannot all hold, or [] if every rule can."""
    names = list(tm.rules)
    tm.model.clear_assumptions()
    tm.model.add_assumptions([tm.rules[n] for n in names])
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1                  # assumptions need a single worker
    if solver.solve(tm.model) != cp_model.INFEASIBLE:
        return []
    by_index = {lit.index: n for n, lit in tm.rules.items()}
    core = [by_index[i] for i in solver.sufficient_assumptions_for_infeasibility()]
    for name in list(core):                            # deletion filter
        rest = [n for n in core if n != name]
        if not holds(tm, rest):
            core = rest
    return sorted(core, key=names.index)               # in the order the rules were made


def why_infeasible(season: Season, overrides: tuple[Override, ...] = ()) -> list[str]:
    tm = build(season, overrides)
    return [tm.says[n] for n in conflict(tm)]
