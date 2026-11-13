"""Turn a season into a plan."""

from __future__ import annotations

from dataclasses import dataclass, field

from vegcrew.data import Season


@dataclass(frozen=True)
class Trim:
    cid: str


@dataclass(frozen=True)
class Plan:
    status: str                                     # OPTIMAL, FEASIBLE, INFEASIBLE or NOT_SOLVED
    trims: dict[str, Trim] = field(default_factory=dict)
    cost: int = 0                                   # $k spent
    risk_removed: int = 0                           # $k a year of risk the trims remove


def make_plan(season: Season) -> Plan:
    """Choose the circuits to trim this year: the most risk removed within the budget.

    Not written yet (lesson 14.1.1).
    """
    return Plan("NOT_SOLVED")
