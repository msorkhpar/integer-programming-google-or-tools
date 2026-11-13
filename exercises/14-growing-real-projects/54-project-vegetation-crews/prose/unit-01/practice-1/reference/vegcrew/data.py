"""The season the planner reads: typed, immutable, and only the columns the planner uses."""

from __future__ import annotations

from dataclasses import dataclass

WEEKS_PER_MONTH = 4     # stub for lesson 14.1.2


@dataclass(frozen=True)
class Circuit:
    cid: str
    region: str
    miles: int
    cost: int           # $k to trim the circuit
    risk: int           # $k a year of tree-caused outage risk that a trim removes


@dataclass(frozen=True)
class Season:
    name: str
    budget: int         # $k for the year's trimming
    circuits: tuple[Circuit, ...]

    def circuit(self, cid: str) -> Circuit:
        return next(c for c in self.circuits if c.cid == cid)


def season_from_dict(raw: dict) -> Season:
    """Read the columns the planner uses. Columns it does not use yet are ignored."""
    circuits = tuple(Circuit(c["id"], c["region"], int(c["miles"]), int(c["cost"]), int(c["risk"]))
                     for c in raw["circuits"])
    return Season(raw.get("name", "season"), int(raw["budget"]), circuits)
