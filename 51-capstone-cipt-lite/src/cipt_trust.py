"""CIPT Lite, milestone 5: one run as a manifest, a harness that reruns it, a golden record, a warm start.

GridCap is a fictional utility's portfolio, generated for this course; none of its numbers are real.

* `run(config)` builds and solves one config and returns its manifest: inputs (the snapshot digest
  and the scenario), solver and parameters, versions, and the result with its work counts. No clock,
  no machine name (lesson 10.2.4).
* `harness(config, runs)` reruns the config in fresh processes, each with its own hash seed, and
  compares the manifests byte for byte (lesson 10.2.5).
* `golden_compare` checks a run against a reviewed record, field by field (lesson 12.3.3).
* `warm_start` maps last cycle's plan onto this cycle's variables, repairs it until no rule breaks,
  and hands it to HiGHS as a solution hint (lessons 4.3.3 and 11.2.1).

Run as `python3 cipt_trust.py '<config json>'` it prints one manifest's canonical bytes: that is the
child process the harness starts.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

from ortools.math_opt.python import mathopt

from cipt_data import digest
from cipt_model import Scenario, build, check, params, plan_of, solve
from gridcap import Portfolio, generate

HERE = Path(__file__).resolve().parent


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def scenario_of(config: dict) -> Scenario:
    s = config.get("scenario", {})
    return Scenario(name=s.get("name", "base"), budget={int(y): v for y, v in s.get("budget", {}).items()})


def repair(pf: Portfolio, sc: Scenario, plan: dict[str, int]) -> dict[str, int]:
    """Drop optional projects, least NPV per $k first, from the years whose limits the plan breaks."""
    plan, by_id = dict(plan), {p.project_id: p for p in pf.projects}
    while broken := check(pf, sc, plan):
        years = {int(r.rsplit("_", 1)[1]) for r in broken if r.startswith(("budget_", "region_", "crews_"))}
        optional = [i for i in plan if not by_id[i].must_do and set(by_id[i].spend(plan[i])) & years]
        if not optional:
            return plan                                      # the caller sees `check` still fail
        drop = min(optional, key=lambda i: (by_id[i].npv[plan[i]] / by_id[i].capex, i))
        for i in [drop] + [c.project_id for c in pf.projects if c.parent == drop]:
            plan.pop(i, None)
    return plan


def warm_start(b, last: dict[str, int]) -> tuple[mathopt.ModelSolveParameters, dict[str, int]]:
    """A complete hint (every start variable 0 or 1) from last cycle's plan, repaired first."""
    carried = {i: t for i, t in last.items() if (i, t) in b.x}
    start = repair(b.portfolio, b.scenario, carried)
    hint = mathopt.SolutionHint(variable_values={v: 1.0 if start.get(pid) == t else 0.0
                                                 for (pid, t), v in b.x.items()})
    return mathopt.ModelSolveParameters(solution_hints=[hint]), start


def run(config: dict) -> dict:
    """Build and solve one config; return its manifest."""
    pf = generate(config["size"])
    sc = scenario_of(config)
    b = build(pf, sc)
    hint = None
    if config.get("hint_from"):                              # last cycle's plan, {project: year}
        hint, _ = warm_start(b, {pid: int(t) for pid, t in config["hint_from"].items()})
    extra = {"time_limit": datetime.timedelta(seconds=config["time_limit"])} if "time_limit" in config else {}
    result = solve(b.model, params(gap=config["gap"], **extra), hint)
    found = result.has_primal_feasible_solution()
    plan = plan_of(b, result) if found else {}
    return {
        "inputs": {"snapshot": digest(pf), "scenario": config.get("scenario", {"name": "base"}),
                   "objective": "npv", "hint_digest": sha(config["hint_from"])[:12] if config.get("hint_from") else None},
        "solver": {"name": "HIGHS", "relative_gap_tolerance": config["gap"], "threads": 1,
                   "time_limit": config.get("time_limit")},
        "versions": {"python": platform.python_version(), "ortools": version("ortools"),
                     "platform": f"{platform.system()}-{platform.machine()}"},
        "result": {"status": result.termination.reason.name,
                   "objective": round(result.objective_value(), 6) if found else None,
                   "bound": round(result.termination.objective_bounds.dual_bound, 6),
                   "plan": sorted([pid, t] for pid, t in plan.items()),
                   "plan_digest": sha(sorted(plan.items()))[:12],
                   "nodes": result.solve_stats.node_count,
                   "simplex_iterations": result.solve_stats.simplex_iterations},
    }


class NotDeterministic(AssertionError):
    pass


def diff(a, b, path: str = "") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in sorted(set(a) | set(b))
                for p in (diff(a.get(k), b.get(k), f"{path}.{k}" if path else k))]
    return [] if a == b else [path]


def child(config: dict, seed: int) -> dict:
    env = {**os.environ, "PYTHONHASHSEED": str(seed),
           "PYTHONPATH": os.pathsep.join([str(HERE), str(Path(sys.modules["gridcap"].__file__).parents[1])])}
    out = subprocess.run([sys.executable, str(HERE / "cipt_trust.py"), json.dumps(config)], env=env,
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def harness(config: dict, runs: int = 10) -> tuple[dict, str]:
    """Raise NotDeterministic unless `runs` fresh processes give byte-identical manifests."""
    manifests = [child(config, seed) for seed in range(1, runs + 1)]
    for k, m in enumerate(manifests[1:], start=2):
        if canonical(m) != canonical(manifests[0]):
            raise NotDeterministic(f"run {k} of {runs} differs at: {', '.join(diff(manifests[0], m))}")
    return manifests[0], sha(manifests[0])


TOLERANCE = 0.01          # $10 of NPV, in $k: far above solver noise, far below one project


def golden_compare(expected: dict, manifest: dict) -> list[str]:
    """One line per difference between a reviewed record and a run, in business terms."""
    out = []
    if expected["snapshot"] != manifest["inputs"]["snapshot"]:
        return [f"input changed: snapshot {expected['snapshot'][:12]} -> {manifest['inputs']['snapshot'][:12]}"]
    r = manifest["result"]
    if expected["status"] != r["status"]:
        out.append(f"status {expected['status']} -> {r['status']}")
    if expected["objective"] is not None and abs(expected["objective"] - r["objective"]) > TOLERANCE:
        out.append(f"objective {expected['objective']:,.2f} -> {r['objective']:,.2f}")
    if expected["plan_digest"] != r["plan_digest"]:
        same = expected["objective"] is not None and abs(expected["objective"] - r["objective"]) <= TOLERANCE
        out.append(f"plan {expected['plan_digest']} -> {r['plan_digest']}" + (" (same value: a tie)" if same else ""))
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.stdout.write(canonical(run(json.loads(sys.argv[1]))).decode("ascii"))
    else:
        manifest = run({"size": "small", "gap": 0.0})
        for section in sorted(manifest):
            for key, value in sorted(manifest[section].items()):
                text = json.dumps(value, sort_keys=True, separators=(",", ":"))
                print(f"{section + '.' + key:<30} {text[:66] + ('...' if len(text) > 66 else '')}")
