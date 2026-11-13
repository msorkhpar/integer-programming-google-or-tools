"""Turn a season into a plan: each trim is one crew's run of consecutive weeks, scheduled by CP-SAT
to carry the least risk, since a circuit's risk grows every week it waits."""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from vegcrew.data import DEFER_WEEKS, WEEKS_PER_MONTH, Season

TIME_LIMIT = 10.0                                   # seconds
WORKERS = 4                                         # parallel search workers


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


def crew_ids(season: Season) -> list[str]:
    return [f"K{k}" for k in range(1, season.crews + 1)]


def horizon(season: Season) -> int:
    return season.months * WEEKS_PER_MONTH


@dataclass
class TrimModel:
    model: cp_model.CpModel
    trimmed: dict[str, cp_model.IntVar] = field(default_factory=dict)                 # circuit
    present: dict[tuple[str, str], cp_model.IntVar] = field(default_factory=dict)    # (circuit, crew)
    start: dict[tuple[str, str], cp_model.IntVar] = field(default_factory=dict)
    work: dict[tuple[str, str], cp_model.IntervalVar] = field(default_factory=dict)
    end: dict[str, cp_model.IntVar] = field(default_factory=dict)                     # circuit
    carried: dict[str, cp_model.IntVar] = field(default_factory=dict)                 # circuit


def build(season: Season) -> TrimModel:
    tm = TrimModel(cp_model.CpModel())
    h = horizon(season)
    deferred = h + DEFER_WEEKS                      # the end week of a circuit left for next season
    for c in season.circuits:
        t = tm.trimmed[c.cid] = tm.model.new_bool_var(f"t_{c.cid}")
        e = tm.end[c.cid] = tm.model.new_int_var_from_domain(
            cp_model.Domain.from_intervals([[c.weeks, h], [deferred, deferred]]), f"e_{c.cid}")
        options = crew_ids(season) if c.weeks <= h else []          # too long for the season: no options
        for k in options:
            p = tm.present[c.cid, k] = tm.model.new_bool_var(f"p_{c.cid}_{k}")
            s = tm.start[c.cid, k] = tm.model.new_int_var(0, h - c.weeks, f"s_{c.cid}_{k}")
            tm.work[c.cid, k] = tm.model.new_optional_fixed_size_interval_var(s, c.weeks, p, f"w_{c.cid}_{k}")
            tm.model.add(e == s + c.weeks).only_enforce_if(p)                        # ends_c,k
        tm.model.add(sum(tm.present[c.cid, k] for k in options) == t)               # once_c
        tm.model.add(e == deferred).only_enforce_if(~t)                              # waits_c
        table = [c.carried(week) for week in range(deferred + 1)]
        tm.carried[c.cid] = tm.model.new_int_var(0, table[-1], f"r_{c.cid}")
        tm.model.add_element(e, table, tm.carried[c.cid])                            # risk_c
    for k in crew_ids(season):
        tm.model.add_no_overlap(w for (_, crew), w in tm.work.items() if crew == k)     # crew_k
    tm.model.add(sum(c.cost * tm.trimmed[c.cid] for c in season.circuits) <= season.budget)   # budget
    tm.model.minimize(sum(tm.carried.values()))
    return tm


def make_plan(season: Season) -> Plan:
    """Choose the circuits to trim, the crew for each and its weeks: the least risk carried through the
    season and the wait for the next, within the budget, one crew per trim, one trim per crew at a time."""
    tm = build(season)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = TIME_LIMIT
    solver.parameters.num_workers = WORKERS
    status = solver.status_name(solver.solve(tm.model))
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
