"""Planning-cycle states and locking for scenarios, kept by a small in-memory service (lesson 12.1.3).

The four stages are lesson 7.1.3's: Initial, Pre-Opt, Post-Opt, Budget Lock. Here they become a
transition table that every request is checked against, a version number that refuses a write made
from a stale read, and a lock that freezes one plan of record per planning cycle. Lesson 12.1.4
moves the same rules into SQLite. The people (`planner-a`, ...) are placeholders.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass

from scenario import Result, Scenario, copy_scenario

STATES = ("Initial", "Pre-Opt", "Post-Opt", "Budget Lock")
ACTIONS = ("edit", "check", "optimize", "lock")
TRANSITIONS = {
    ("Initial", "edit"): "Initial",
    ("Initial", "check"): "Pre-Opt",
    ("Pre-Opt", "edit"): "Pre-Opt",
    ("Pre-Opt", "optimize"): "Post-Opt",
    ("Post-Opt", "edit"): "Pre-Opt",
    ("Post-Opt", "optimize"): "Post-Opt",
    ("Post-Opt", "lock"): "Budget Lock",
}


class Refused(Exception):
    """A request the cycle's rules do not allow; the message says which rule."""


@dataclass
class Record:
    scenario: Scenario
    cycle: str
    state: str = "Initial"
    version: int = 1
    result: Result | None = None
    locked_by: str | None = None


@dataclass(frozen=True)
class Ticket:
    """A run in progress: which scenario, at which version, on which inputs."""

    scenario_id: str
    version: int
    inputs: Scenario


class Service:
    def __init__(self):
        self.records: dict[str, Record] = {}
        self.log: list[str] = []

    def _move(self, rec: Record, action: str) -> None:
        nxt = TRANSITIONS.get((rec.state, action))
        if nxt is None:
            raise Refused(f"{rec.scenario.scenario_id} is {rec.state}; {action} is not allowed there")
        rec.state = nxt

    def _current(self, sid: str, expected_version: int) -> Record:
        rec = self.records[sid]
        if rec.version != expected_version:
            raise Refused(f"{sid} is at version {rec.version}, not {expected_version}; read it again")
        return rec

    def add(self, s: Scenario, cycle: str) -> int:
        self.records[s.scenario_id] = Record(copy.deepcopy(s), cycle)
        return 1

    def read(self, sid: str) -> tuple[Scenario, str, int]:
        """A private copy of the scenario, its state and its version: editing the copy changes nothing stored."""
        rec = self.records[sid]
        return copy.deepcopy(rec.scenario), rec.state, rec.version

    def edit(self, sid: str, expected_version: int, changed: Scenario) -> int:
        rec = self._current(sid, expected_version)
        self._move(rec, "edit")
        rec.scenario, rec.version = copy.deepcopy(changed), rec.version + 1
        return rec.version

    def check(self, sid: str, expected_version: int) -> int:
        rec = self._current(sid, expected_version)
        self._move(rec, "check")
        rec.version += 1
        return rec.version

    def start_run(self, sid: str) -> Ticket:
        rec = self.records[sid]
        if (rec.state, "optimize") not in TRANSITIONS:
            raise Refused(f"{sid} is {rec.state}; optimize is not allowed there")
        return Ticket(sid, rec.version, copy.deepcopy(rec.scenario))

    def finish_run(self, ticket: Ticket, result: Result) -> int:
        """Attach a finished run, unless the scenario was changed while it ran."""
        rec = self._current(ticket.scenario_id, ticket.version)
        self._move(rec, "optimize")
        rec.result, rec.version = result, rec.version + 1
        return rec.version

    def lock(self, sid: str, expected_version: int, by: str) -> int:
        rec = self._current(sid, expected_version)
        if (rec.state, "lock") not in TRANSITIONS:
            raise Refused(f"{sid} is {rec.state}; lock is not allowed there")
        if rec.result is None or rec.result.snapshot != rec.scenario.snapshot():
            raise Refused(f"{sid} has no run on its current inputs")
        if rec.result.status != "OPTIMAL":
            raise Refused(f"{sid}'s run is {rec.result.status}, not a plan")
        for other in self.records.values():
            if other.cycle == rec.cycle and other.state == "Budget Lock":
                raise Refused(f"{rec.cycle} already has a plan of record: {other.scenario.scenario_id}")
        self._move(rec, "lock")
        rec.locked_by, rec.version = by, rec.version + 1
        return rec.version

    def copy(self, sid: str, new_id: str, name: str, by: str, at: str) -> int:
        """Any scenario may be copied, a locked one included; the copy starts again in Initial."""
        rec = self.records[sid]
        return self.add(copy_scenario(rec.scenario, new_id, name, by, at), rec.cycle)
