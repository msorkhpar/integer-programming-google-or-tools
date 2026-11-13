"""Planner overrides as bounds on start variables, with an append-only audit trail (lesson 12.1.2).

An `Override` says only what the model needs: which project, which kind, which year. Who asked,
when and why live in the `AuditEntry` that recorded it, together with the bounds it changed.
GridCap is a fictional utility's portfolio; the overrides and the people (`planner-a`, ...) are
invented for the course.
"""

from __future__ import annotations

from dataclasses import dataclass

from gridcap import Portfolio, Project

KINDS = ("start_in", "out", "not_before", "not_after")
FREE = (0, 1)


@dataclass(frozen=True)
class Override:
    project: str
    kind: str                 # one of KINDS
    year: int | None = None   # None for "out"

    def text(self) -> str:
        return f"{self.project} {self.kind}" + (f" {self.year}" if self.year is not None else "")


def bounds_of(o: Override, p: Project) -> dict[tuple[str, int], tuple[int, int]]:
    """The (lower, upper) bounds the override puts on each of the project's start variables."""
    bounds = {}
    for t in p.starts():
        if o.kind == "start_in":
            bounds[p.project_id, t] = (1, 1) if t == o.year else (0, 0)
        elif o.kind == "out" or (o.kind == "not_before" and t < o.year) or (o.kind == "not_after" and t > o.year):
            bounds[p.project_id, t] = (0, 0)
        else:
            bounds[p.project_id, t] = FREE
    return bounds


def check(o: Override, portfolio: Portfolio) -> list[str]:
    """Why the override cannot be accepted as it stands; empty when it can."""
    if o.project not in portfolio.project_ids:
        return [f"{o.project} is not in the portfolio"]
    if o.kind not in KINDS:
        return [f"{o.kind!r} is not an override kind; use one of {', '.join(KINDS)}"]
    p = portfolio.project(o.project)
    window = f"{p.earliest_start}-{p.latest_start}"
    if o.kind != "out" and o.year is None:
        return [f"{o.kind} needs a year"]
    if o.kind == "start_in" and o.year not in p.starts():
        return [f"{o.project} cannot start in {o.year}: its window is {window}"]
    leaves_none = all(b == (0, 0) for b in bounds_of(o, p).values())
    if o.kind in ("not_before", "not_after") and leaves_none:
        return [f"{o.text()} leaves {o.project} no start year in {window}"]
    if p.must_do and leaves_none:
        return [f"{o.project} is a must-do and cannot be overridden out"]
    return []


@dataclass(frozen=True)
class AuditEntry:
    seq: int
    scenario_id: str
    action: str                  # "set", "revoke", "inherit" or "refused"
    override: Override
    by: str
    at: str                      # ISO 8601, UTC
    why: str
    changes: tuple[str, ...]     # "x_P024_2028 [0,1] -> [0,0]", or the reasons it was refused

    def line(self) -> str:
        return f"#{self.seq} {self.at} {self.by:<9} {self.action:<7} {self.override.text():<20} {self.why}"


def bound_changes(old: Override | None, new: Override | None, p: Project) -> tuple[str, ...]:
    """Each start variable whose bounds move when `old` is replaced by `new` (None: no override)."""
    before = bounds_of(old, p) if old else {(p.project_id, t): FREE for t in p.starts()}
    after = bounds_of(new, p) if new else {(p.project_id, t): FREE for t in p.starts()}
    return tuple(f"x_{pid}_{t} [{before[pid, t][0]},{before[pid, t][1]}] -> [{after[pid, t][0]},{after[pid, t][1]}]"
                 for (pid, t) in sorted(before) if before[pid, t] != after[pid, t])


def replay(trail: list[AuditEntry], scenario_id: str) -> dict[str, Override]:
    """The overrides in force for a scenario, rebuilt from its audit trail alone."""
    active: dict[str, Override] = {}
    for e in sorted(trail, key=lambda e: e.seq):
        if e.scenario_id != scenario_id:
            continue
        if e.action in ("set", "inherit"):
            active[e.override.project] = e.override
        elif e.action == "revoke":
            active.pop(e.override.project, None)
    return active


def request(s, trail: list[AuditEntry], o: Override, portfolio: Portfolio, by: str, at: str, why: str) -> AuditEntry:
    """Record a planner's override on scenario `s`: accepted as bounds, or refused with the reasons."""
    problems = check(o, portfolio)
    if problems:
        entry = AuditEntry(len(trail) + 1, s.scenario_id, "refused", o, by, at, why, tuple(problems))
    else:
        changes = bound_changes(s.overrides.get(o.project), o, portfolio.project(o.project))
        entry = AuditEntry(len(trail) + 1, s.scenario_id, "set", o, by, at, why, changes)
        s.overrides[o.project] = o
    trail.append(entry)
    return entry


def revoke(s, trail: list[AuditEntry], project: str, portfolio: Portfolio, by: str, at: str, why: str) -> AuditEntry:
    """Take an override back. The entry that set it stays; this one records that it ended."""
    old = s.overrides.pop(project)
    entry = AuditEntry(len(trail) + 1, s.scenario_id, "revoke", old, by, at, why,
                       bound_changes(old, None, portfolio.project(project)))
    trail.append(entry)
    return entry
