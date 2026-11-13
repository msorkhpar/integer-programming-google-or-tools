"""The manual lexicographic solve: one pass per objective, each kept within its tolerance.

`Level` names one objective of `lex_model.StartModel` with its sense and tolerances. `solve_levels`
optimizes the levels in order and, after each pass, adds the row that keeps that objective within
its allowed loss of the best value just found. It deletes the rows again before it returns, so the
caller's model is the one it was given. Each kept row is loosened by `TOL`, a numerical slack far
below any tolerance a planner sets: a solver can report a pass's best a hair above the value of the
plan it returned (`kept_row.py` shows one), and the row must not exclude that plan. GridCap is a
fictional utility's portfolio.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from lex_model import StartModel, plan_of, solve

TOL = 1e-6        # numerical slack on every kept row, so pass k's own plan always meets it


@dataclass(frozen=True)
class Level:
    name: str                 # "npv", "risk" or "spend"
    maximize: bool = True
    abs_tol: float = 0.0      # $k the objective may lose
    rel_tol: float = 0.0      # share of |best| the objective may lose


@dataclass
class Outcome:
    plan: dict[str, int]                                       # project id -> start year
    best: dict[str, float] = field(default_factory=dict)       # each pass's optimum
    floor: dict[str, float] = field(default_factory=dict)      # each kept row's bound, before TOL


def allowed_loss(best: float, level: Level) -> float:
    """The larger of the two tolerances: meeting either one is enough."""
    return max(level.abs_tol, level.rel_tol * abs(best))


def solve_levels(sm: StartModel, levels: list[Level], gap: float = 0.0) -> Outcome:
    """Optimize each level in turn; every pass keeps the earlier ones within their tolerances."""
    kept, outcome = [], Outcome(plan={})
    for level in levels:
        expr = sm.objective(level.name)
        sm.model.set_linear_objective(expr, is_maximize=level.maximize)
        result = solve(sm.model, gap)                                   # pass k
        best = result.objective_value()
        loss = allowed_loss(best, level)
        if level.maximize:
            row, bound = expr >= best - loss - TOL, best - loss
        else:
            row, bound = expr <= best + loss + TOL, best + loss
        kept.append(sm.model.add_linear_constraint(row, name=f"keep_{level.name}"))
        outcome.best[level.name], outcome.floor[level.name] = best, bound
    outcome.plan = plan_of(sm, result)
    for row in kept:                                                    # give the model back as it was
        sm.model.delete_linear_constraint(row)
    return outcome
