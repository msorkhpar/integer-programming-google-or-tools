"""Snapshots, scenarios and runs in one SQLite file. Stub: lesson 14.2.7 writes the methods.

The schema is given; the methods store and return nothing yet.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .plan import Plan
from .scenario import Scenario

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshot (hash TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scenario (name TEXT PRIMARY KEY, snapshot TEXT NOT NULL REFERENCES snapshot(hash),
                                     body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS run (id INTEGER PRIMARY KEY, scenario TEXT NOT NULL REFERENCES scenario(name),
                                snapshot TEXT NOT NULL, status TEXT NOT NULL, npv REAL, risk REAL,
                                starts TEXT NOT NULL);
"""


class Store:
    def __init__(self, path: str | Path) -> None:
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)

    def save_snapshot(self, raw: dict) -> str:
        """Store the export under its hash. Stub."""
        return ""

    def snapshot(self, digest: str) -> dict:
        """The stored export, checked against its hash. Stub."""
        return {}

    def save_scenario(self, scenario: Scenario, snapshot: str) -> None:
        """Store a scenario beside its snapshot. Stub."""

    def run(self, name: str) -> Plan:
        """Plan a stored scenario and store the run. Stub."""
        return Plan(status="not solved")

    def runs(self, name: str) -> list[Plan]:
        """Every stored run of a scenario. Stub."""
        return []
