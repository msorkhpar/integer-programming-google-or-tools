"""Turn a season into a plan: each trim is one crew's run of consecutive weeks, scheduled by CP-SAT
to carry the least risk, keeping every calendar, must and planner's override, or saying why it cannot."""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from vegcrew.data import Override, Season
from vegcrew.explain import why_infeasible
from vegcrew.model import build, crew_ids, horizon

TIME_LIMIT = 10.0                                   # seconds
WORKERS = 4                                         # parallel search workers

__all__ = ["Plan", "Trim", "check_overrides", "crew_ids", "horizon", "make_plan"]


@dataclass(frozen=True)
class Trim:
    cid: str
    crew: str                                       # K1, K2, ...
    start: int                                      # first week, counted from 0
    end: int                                        # the week after the last: end - start = weeks


@dataclass(frozen=True)
class Plan:
    status: str                                     # OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN or MODEL_INVALID
    trims: dict[str, Trim] = field(default_factory=dict)
    cost: int = 0                                   # $k spent
    risk_removed: int = 0                           # $k a year of risk the trims remove
    risk_carried: int = 0                           # $k of risk carried until each circuit is trimmed
    explanation: tuple[str, ...] = ()               # INFEASIBLE: the rules that cannot all hold


def check_overrides(season: Season, overrides: tuple[Override, ...]) -> list[str]:
    """What is wrong with the overrides as data, before any model is built."""
    problems = []
    ids = {c.cid for c in season.circuits}
    for i, o in enumerate(overrides, start=1):
        if o.kind not in ("pin", "skip", "force"):
            problems.append(f"override {i}: unknown kind {o.kind!r}")
        if o.cid not in ids:
            problems.append(f"override {i}: no circuit {o.cid}")
        if o.crew is not None and o.crew not in crew_ids(season):
            problems.append(f"override {i}: no crew {o.crew}")
        if o.start is not None and not 0 <= o.start < horizon(season):
            problems.append(f"override {i}: week {o.start} is outside the season")
    return problems


def make_plan(season: Season, overrides: tuple[Override, ...] = ()) -> Plan:
    """Choose the circuits to trim, the crew for each and its weeks: the least risk carried through the
    season and the wait for the next, within the budget, one crew per trim, one trim per crew at a time,
    every trim inside one of its circuit's windows and outside its crew's weeks off, every must trimmed,
    every override kept. If no plan keeps every rule, say which of the planner's rules clash."""
    problems = check_overrides(season, overrides)
    if problems:
        raise ValueError("; ".join(problems))
    tm = build(season, overrides)
    tm.model.add_bool_and(list(tm.rules.values()))     # every rule holds
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = TIME_LIMIT
    solver.parameters.num_workers = WORKERS
    status = solver.status_name(solver.solve(tm.model))
    if status == "INFEASIBLE":
        return Plan(status, explanation=tuple(why_infeasible(season, overrides)))
    if status not in ("OPTIMAL", "FEASIBLE"):
        return Plan(status)
    trims = {}
    for (cid, k), p in tm.present.items():
        if solver.boolean_value(p):
            start = solver.value(tm.start[cid, k])
            trims[cid] = Trim(cid, k, start, start + season.circuit(cid).weeks)
    chosen = [season.circuit(cid) for cid in trims]
    return Plan(status, trims, cost=sum(c.cost for c in chosen), risk_removed=sum(c.risk for c in chosen),
                risk_carried=round(solver.objective_value))
