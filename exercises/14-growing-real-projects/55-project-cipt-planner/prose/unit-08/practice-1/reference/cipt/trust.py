"""Trust at scale: a run manifest, a determinism harness and a golden check (lessons 10.2.4-10.2.5, 12.3.3).

A plan is identified by the sha256 of its canonical JSON (status and starts), so two runs agree
exactly when their digests do. The manifest records what a run depended on: the export's hash,
the scenario, the solver and its settings, and the plan's digest. The golden file is a reviewed
plan for a fixed export; a change in the code that changes that plan fails the check until someone
reviews the new plan and writes it as the new golden.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import ortools

from .data import load_request
from .plan import Plan
from .scenario import Scenario, apply
from .solve import PARAMS, solve
from .store import canonical, content_hash


def plan_digest(plan: Plan) -> str:
    body = canonical({"status": plan.status, "starts": plan.starts})
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def manifest(raw: dict, scenario: Scenario, plan: Plan) -> dict:
    return {
        "input": content_hash(raw),
        "scenario": scenario.to_dict(),
        "solver": {"name": "HIGHS", "ortools": ortools.__version__,
                   "threads": PARAMS.highs.int_options["threads"]},
        "plan": plan_digest(plan),
        "npv": round(plan.npv, 2),
    }


@dataclass(frozen=True)
class Harness:
    digests: list[str]

    @property
    def same(self) -> bool:
        return len(self.digests) > 1 and len(set(self.digests)) == 1


def harness(raw: dict, runs: int = 3, scenario: Scenario = Scenario("base")) -> Harness:
    """Plan the same export `runs` times from scratch and keep each plan's digest."""
    return Harness([plan_digest(solve(apply(load_request(raw), scenario))) for _ in range(runs)])


def write_golden(raw: dict, path: str | Path) -> None:
    plan = solve(load_request(raw))
    Path(path).write_text(json.dumps({"input": content_hash(raw), "status": plan.status, "npv": plan.npv,
                                      "starts": plan.starts}, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def check_golden(raw: dict, path: str | Path) -> list[str]:
    """Every way today's plan of `raw` differs from the golden one; empty when they agree."""
    golden = json.loads(Path(path).read_text(encoding="utf-8"))
    if golden["input"] != content_hash(raw):
        return [f"input changed: golden {golden['input'][:12]}, now {content_hash(raw)[:12]}"]
    plan = solve(load_request(raw))
    found = [] if plan.status == golden["status"] else [f"status {golden['status']} -> {plan.status}"]
    for pid in sorted(set(golden["starts"]) | set(plan.starts)):
        before, now = golden["starts"].get(pid), plan.starts.get(pid)
        if before != now:
            found.append(f"{pid}: start {before} -> {now}")
    if abs(plan.npv - golden["npv"]) > 0.5:
        found.append(f"npv {golden['npv']:,.0f} -> {plan.npv:,.0f}")
    return found


def warm_solve(raw: dict, previous: Plan) -> Plan:
    """Plan `raw` starting from last cycle's plan."""
    return solve(load_request(raw), previous=previous)
