"""Milestone 5: a run's manifest, and a harness that reruns it in fresh processes.

The practice portfolio is a fictional utility's, invented for this exercise.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from importlib.metadata import version

from ortools.sat.python import cp_model

# ---- given: the practice portfolio and a CP-SAT solve (milestone 2's rules, reduced) -------------

SNAPSHOT = {
    "years": [2027, 2028, 2029], "rate": 0.05,
    "budget": {2027: 300, 2028: 300, 2029: 300},
    "projects": {
        "J1": {"cost": [100], "earliest": 2027, "latest": 2029, "must": True, "npv": {2027: 40, 2028: 38, 2029: 36}},
        "J2": {"cost": [100], "earliest": 2027, "latest": 2028, "must": False, "npv": {2027: 30, 2028: 29}},
        "J3": {"cost": [100], "earliest": 2027, "latest": 2029, "must": False, "npv": {2027: 30, 2028: 28, 2029: 27}},
        "J4": {"cost": [100, 100], "earliest": 2027, "latest": 2028, "must": False, "npv": {2027: 55, 2028: 50}},
        "J5": {"cost": [100], "earliest": 2028, "latest": 2029, "must": False, "npv": {2028: 25, 2029: 24}},
        "J6": {"cost": [100], "earliest": 2027, "latest": 2029, "must": False, "npv": {2027: 22, 2028: 21, 2029: 20}},
        "J7": {"cost": [100, 100], "earliest": 2028, "latest": 2028, "must": False, "npv": {2028: 45}},
        "J8": {"cost": [100], "earliest": 2029, "latest": 2029, "must": False, "npv": {2029: 18}},
    },
}


def solve(snapshot: dict, objective: str = "npv", order: str = "sorted", seed: int = 0) -> dict:
    """Best plan by CP-SAT on one worker. `order` "set" builds the projects in a set's order."""
    ids = list(set(snapshot["projects"])) if order == "set" else sorted(snapshot["projects"])
    m = cp_model.CpModel()
    x = {(j, t): m.new_bool_var(f"x_{j}_{t}") for j in ids
         for t in range(snapshot["projects"][j]["earliest"], snapshot["projects"][j]["latest"] + 1)}
    for j in ids:
        mine = [v for (i, _), v in x.items() if i == j]
        m.add(sum(mine) == 1) if snapshot["projects"][j]["must"] else m.add(sum(mine) <= 1)
    for y in snapshot["years"]:
        m.add(sum(c * v for (j, t), v in x.items() for k, c in enumerate(snapshot["projects"][j]["cost"])
                  if t + k == y) <= snapshot["budget"][y])
    if objective == "count":
        m.maximize(sum(x.values()))
    else:
        m.maximize(sum(snapshot["projects"][j]["npv"][t] * v for (j, t), v in x.items()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = seed
    status = solver.solve(m)
    return {"status": solver.status_name(status), "objective": solver.objective_value,
            "plan": {j: t for (j, t), v in x.items() if solver.value(v)},
            "branches": solver.num_branches, "conflicts": solver.num_conflicts}


def snapshot_for(config: dict) -> dict:
    """The practice portfolio with the config's budget overrides ({"2028": 200}) applied."""
    budget = {**SNAPSHOT["budget"], **{int(y): v for y, v in config.get("budget", {}).items()}}
    return {**SNAPSHOT, "budget": budget}


# ---- yours -----------------------------------------------------------------------------------------


class NotDeterministic(AssertionError):
    """Two runs of one config gave manifests with different bytes."""


def canonical(obj) -> bytes:
    """One byte string per value: sorted keys, no spaces, ASCII only."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def manifest(config: dict) -> dict:
    """What went in and what came out of one run, and nothing about the clock or the machine's owner."""
    snapshot = snapshot_for(config)
    objective, order, seed = config.get("objective", "npv"), config.get("order", "sorted"), config.get("seed", 0)
    result = solve(snapshot, objective, order, seed)
    return {
        "inputs": {"snapshot": hashlib.sha256(canonical(snapshot)).hexdigest(), "objective": objective,
                   "order": order},
        "solver": {"name": "CP-SAT", "num_workers": 1, "random_seed": seed},
        "versions": {"python": platform.python_version(), "ortools": version("ortools")},
        "result": {"status": result["status"], "objective": result["objective"],
                   "plan": sorted([j, t] for j, t in result["plan"].items()),
                   "branches": result["branches"], "conflicts": result["conflicts"]},
    }


def differences(a, b, path: str = "") -> list[str]:
    """The dotted paths at which two manifests differ; a list is compared whole."""
    if isinstance(a, dict) and isinstance(b, dict):
        found = []
        for key in sorted(set(a) | set(b)):
            found += differences(a.get(key), b.get(key), f"{path}.{key}" if path else key)
        return found
    return [] if a == b else [path]


def run_in_child(config: dict, seed: int) -> bytes:
    """One run in a fresh Python process whose hash seed is `seed`; its manifest's canonical bytes."""
    env = {**os.environ, "PYTHONHASHSEED": str(seed)}
    return subprocess.run([sys.executable, __file__, json.dumps(config)], env=env, capture_output=True,
                          check=True).stdout


def harness(config: dict, runs: int = 10) -> str:
    """Run `config` in `runs` fresh processes; return the manifest's sha256, or raise NotDeterministic."""
    outputs = [run_in_child(config, seed) for seed in range(1, runs + 1)]
    for k, out in enumerate(outputs[1:], start=2):
        if out != outputs[0]:
            changed = differences(json.loads(outputs[0]), json.loads(out))
            raise NotDeterministic(f"run {k} of {runs} differs at: {', '.join(changed)}")
    return hashlib.sha256(outputs[0]).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.stdout.write(canonical(manifest(json.loads(sys.argv[1]))).decode("ascii"))
    else:
        print(harness({"objective": "npv"}, runs=3))
