"""Lesson 12.2.2: data-quality rules that run on a validated Snapshot, before the model is built.

Each rule reads the snapshot (and, for drift, the last accepted snapshot) and returns Findings.
An error blocks the solve; a warning goes into the run's report. GridCap is a fictional utility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from plan_model import starts
from snapshot import Snapshot

Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: Severity
    subject: str
    detail: str


def parent_cycle(snap: Snapshot, previous: Snapshot | None) -> list[Finding]:
    """A project that is, through its parents, its own ancestor."""
    parent = {p.project_id: p.parent for p in snap.projects}
    found, seen = [], set()
    for start in sorted(parent):
        path, pid = [], start
        while pid is not None and pid not in path:
            path.append(pid)
            pid = parent.get(pid)
        if pid is not None:                                     # came back to a project on the path
            loop = path[path.index(pid):]
            if frozenset(loop) not in seen:
                seen.add(frozenset(loop))
                found.append(Finding("parent-cycle", "error", " -> ".join(loop + [pid]),
                                     "a project cannot be a prerequisite of its own prerequisite"))
    return found


def parent_too_late(snap: Snapshot, previous: Snapshot | None) -> list[Finding]:
    """A child whose parent cannot start early enough for any of the child's start years."""
    by_id = {p.project_id: p for p in snap.projects}
    found = []
    for c in snap.projects:
        if not c.parent:
            continue
        mine, theirs = starts(c, snap.years), starts(by_id[c.parent], snap.years)
        if mine and theirs and min(theirs) + c.parent_lag <= max(mine):
            continue
        severity = "error" if c.must_do else "warning"
        found.append(Finding("parent-too-late", severity, c.project_id,
                             f"parent {c.parent} starts {theirs}, lag {c.parent_lag}; child starts {mine}"))
    return found


def required(snap: Snapshot) -> set[str]:
    """Must-do projects and, through the precedence rows, every ancestor of one."""
    parent = {p.project_id: p.parent for p in snap.projects}
    need = set()
    for pid in (p.project_id for p in snap.projects if p.must_do):
        while pid is not None and pid not in need:
            need.add(pid)
            pid = parent[pid]
    return need


def required_over_budget(snap: Snapshot, previous: Snapshot | None) -> list[Finding]:
    """The projects every plan must fund cost more than all the plan's budgets together."""
    cost = {p.project_id: sum(p.cost_profile) for p in snap.projects}
    need = sum(cost[pid] for pid in required(snap))
    total = sum(b.amount for b in snap.budget)
    if need <= total:
        return []
    return [Finding("required-over-budget", "error", "plan",
                    f"required projects cost ${need:,}k; all budgets together ${total:,}k")]


def pulls_in_parent(snap: Snapshot, previous: Snapshot | None) -> list[Finding]:
    """A must-do child whose parent is optional: the model will fund the parent anyway."""
    by_id = {p.project_id: p for p in snap.projects}
    return [Finding("pulls-in-parent", "warning", c.project_id,
                    f"must-do, so its optional parent {c.parent} becomes required too")
            for c in snap.projects if c.must_do and c.parent and not by_id[c.parent].must_do]


def budget_drift(snap: Snapshot, previous: Snapshot | None, factor: float = 3.0) -> list[Finding]:
    """A year's budget more than `factor` times larger or smaller than in the last accepted snapshot."""
    if previous is None:
        return []
    before = {b.year: b.amount for b in previous.budget}
    found = []
    for b in snap.budget:
        old = before.get(b.year)
        if old and (b.amount > factor * old or b.amount * factor < old):
            found.append(Finding("budget-drift", "warning", str(b.year),
                                 f"${old:,}k last snapshot, ${b.amount:,}k now"))
    return found


RULES: list[Callable[[Snapshot, Snapshot | None], list[Finding]]] = [
    parent_cycle, parent_too_late, required_over_budget, pulls_in_parent, budget_drift]


def gate(snap: Snapshot, previous: Snapshot | None = None) -> list[Finding]:
    """Run every rule and return every finding, errors first. Never stops at the first one."""
    found = [f for rule in RULES for f in rule(snap, previous)]
    return sorted(found, key=lambda f: (f.severity != "error", f.rule, f.subject))


def blocked(findings: list[Finding]) -> bool:
    return any(f.severity == "error" for f in findings)


def report(findings: list[Finding]) -> None:
    if not findings:
        print("   gate: no finding")
    for f in findings:
        print(f"   {f.severity:<7} {f.rule:<20} {f.subject:<22} {f.detail}")
