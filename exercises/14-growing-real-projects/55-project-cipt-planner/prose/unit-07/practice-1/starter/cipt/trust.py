"""Trust at scale. Stub: lesson 14.2.8 writes it; until then nothing is checked."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .plan import Plan
from .scenario import Scenario


def plan_digest(plan: Plan) -> str:
    """The sha256 of the plan's canonical JSON. Stub."""
    return ""


def manifest(raw: dict, scenario: Scenario, plan: Plan) -> dict:
    """What a run depended on. Stub."""
    return {}


@dataclass(frozen=True)
class Harness:
    digests: list[str]

    @property
    def same(self) -> bool:
        return len(self.digests) > 1 and len(set(self.digests)) == 1


def harness(raw: dict, runs: int = 3, scenario: Scenario = Scenario("base")) -> Harness:
    """Plan the same export `runs` times. Stub: no runs."""
    return Harness([])


def write_golden(raw: dict, path: str | Path) -> None:
    """Write today's plan as the golden one. Stub."""


def check_golden(raw: dict, path: str | Path) -> list[str]:
    """How today's plan differs from the golden one. Stub: never checked."""
    return ["not checked"]


def warm_solve(raw: dict, previous: Plan) -> Plan:
    """Plan `raw` starting from last cycle's plan. Stub."""
    return Plan(status="not solved")
