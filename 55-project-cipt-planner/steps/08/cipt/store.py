"""Snapshots, scenarios and runs in one SQLite file (lesson 12.1.4).

A snapshot is the export exactly as received, stored as canonical JSON under the sha256 of that
JSON, so a run can always be traced to the bytes it planned from, and a changed byte is caught when
the snapshot is read. A run stores the scenario, the snapshot's hash and the plan it produced.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from .data import load_request
from .plan import Plan
from .scenario import Scenario, apply
from .solve import solve

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshot (hash TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scenario (name TEXT PRIMARY KEY, snapshot TEXT NOT NULL REFERENCES snapshot(hash),
                                     body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS run (id INTEGER PRIMARY KEY, scenario TEXT NOT NULL REFERENCES scenario(name),
                                snapshot TEXT NOT NULL, status TEXT NOT NULL, npv REAL, risk REAL,
                                starts TEXT NOT NULL);
"""


def canonical(raw: dict) -> str:
    return json.dumps(raw, sort_keys=True, separators=(",", ":"))


def content_hash(raw: dict) -> str:
    return hashlib.sha256(canonical(raw).encode("utf-8")).hexdigest()


class Store:
    def __init__(self, path: str | Path) -> None:
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)

    def save_snapshot(self, raw: dict) -> str:
        digest = content_hash(raw)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO snapshot VALUES (?, ?)", (digest, canonical(raw)))
        return digest

    def snapshot(self, digest: str) -> dict:
        (body,) = self.db.execute("SELECT body FROM snapshot WHERE hash = ?", (digest,)).fetchone()
        raw = json.loads(body)
        if content_hash(raw) != digest:
            raise ValueError(f"snapshot {digest[:12]} does not match its hash")
        return raw

    def save_scenario(self, scenario: Scenario, snapshot: str) -> None:
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO scenario VALUES (?, ?, ?)",
                            (scenario.name, snapshot, canonical(scenario.to_dict())))

    def scenario(self, name: str) -> tuple[Scenario, str]:
        body, snapshot = self.db.execute("SELECT body, snapshot FROM scenario WHERE name = ?", (name,)).fetchone()
        return Scenario.from_dict(json.loads(body)), snapshot

    def run(self, name: str) -> Plan:
        """Plan a stored scenario from its snapshot, and store the run."""
        scenario, snapshot = self.scenario(name)
        plan = solve(apply(load_request(self.snapshot(snapshot)), scenario))
        with self.db:
            self.db.execute("INSERT INTO run (scenario, snapshot, status, npv, risk, starts) VALUES (?, ?, ?, ?, ?, ?)",
                            (name, snapshot, plan.status, plan.npv, plan.risk, canonical(plan.starts)))
        return plan

    def runs(self, name: str) -> list[Plan]:
        found = self.db.execute("SELECT status, npv, risk, starts FROM run WHERE scenario = ? ORDER BY id", (name,))
        return [Plan(status=s, starts=json.loads(starts), objective=npv, npv=npv, risk=risk)
                for s, npv, risk, starts in found]
