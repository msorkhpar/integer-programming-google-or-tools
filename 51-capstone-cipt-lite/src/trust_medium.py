"""Lesson 13.1.5: the determinism harness, the golden records and the warm start, on GridCap medium.

1. Ten fresh processes solve GridCap medium with the run setting; their manifests must be byte for
   byte the same. A known-bad config (a 2-second clock limit) must fail the same harness.
2. Three golden records, reviewed once and stored in golden/cipt_golden.json, are compared with
   fresh runs; then with a run whose gap someone loosened to 1%.
3. Finance cuts 2028 to $40,000k. Last cycle's plan breaks the cut; repaired, it warm-starts the
   solve. The hinted run goes through the harness too.

`python3 trust_medium.py --write-golden` rewrites the golden file; review its diff before committing.
GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cipt_model import Scenario, build, check, params, plan_of, solve
from cipt_trust import NotDeterministic, golden_compare, harness, run, warm_start
from gridcap import generate

GOLDEN = Path(__file__).resolve().parent / "golden" / "cipt_golden.json"
CUT = {"name": "2028-cut", "budget": {"2028": 40_000}}
CONFIGS = {
    "small-base": {"size": "small", "gap": 0.0},
    "small-2028-cut": {"size": "small", "gap": 0.0, "scenario": {"name": "2028-cut", "budget": {"2028": 6_000}}},
    "medium-base": {"size": "medium", "gap": 1e-3},
}


def record(manifest: dict) -> dict:
    r = manifest["result"]
    return {"snapshot": manifest["inputs"]["snapshot"], "status": r["status"], "objective": r["objective"],
            "plan_digest": r["plan_digest"], "projects": len(r["plan"])}


if __name__ == "__main__":
    if sys.argv[1:] == ["--write-golden"]:
        GOLDEN.parent.mkdir(exist_ok=True)
        records = {name: record(run(config)) for name, config in CONFIGS.items()}
        GOLDEN.write_text(json.dumps(records, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        sys.exit(0)

    print("1. determinism")
    manifest, key = harness(CONFIGS["medium-base"], runs=10)
    r = manifest["result"]
    print(f"   PASS medium, gap 0.1%, 1 thread: 10 identical manifests, sha256 {key[:16]}, "
          f"{r['status']} {r['objective']:,.0f}, {r['nodes']:,} nodes")
    try:
        harness({"size": "medium", "gap": 0.0, "time_limit": 2.0}, runs=3)
        print("   PASS medium, zero gap, 2 s clock limit")
    except NotDeterministic as error:
        print("   FAIL medium, zero gap, 2 s clock limit: NotDeterministic")
        print(f"        {error}")

    print("2. golden records")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    for name, config in CONFIGS.items():
        found = golden_compare(golden[name], run(config))
        print(f"   {name:<15} {'same as reviewed' if not found else '; '.join(found)}")
    loose_config = {**CONFIGS["medium-base"], "gap": 1e-2}
    loose_run = run(loose_config)
    print(f"   {'medium, gap 1%':<15} {'; '.join(golden_compare(golden['medium-base'], loose_run))}")
    loose_plan = {pid: t for pid, t in loose_run["result"]["plan"]}
    _, key = harness(loose_config, runs=10)
    print(f"   the gap-1% plan breaks {check(generate('medium'), Scenario(), loose_plan) or 'no rule'}; "
          f"harness: 10 identical manifests, sha256 {key[:16]}")

    print("3. warm start after a 2028 cut to $40,000k")
    medium = generate("medium")
    last = {pid: t for pid, t in manifest["result"]["plan"]}
    cut = build(medium, Scenario(name="2028-cut", budget={2028: 40_000}))
    print(f"   last cycle's plan: {len(last)} projects, breaks {check(medium, cut.scenario, last)}")
    hint, start = warm_start(cut, last)
    print(f"   repaired start: {len(start)} projects, breaks {check(medium, cut.scenario, start) or 'nothing'}")
    for label, model_params in (("no hint", None), ("hinted", hint)):
        result = solve(cut.model, params(gap=1e-3), model_params)
        print(f"   {label:<8} {result.termination.reason.name}, NPV {result.objective_value():,.0f}, "
              f"{result.solve_stats.node_count:,} nodes")
    _, key = harness({"size": "medium", "gap": 1e-3, "scenario": CUT, "hint_from": last}, runs=10)
    print(f"   PASS hinted run: 10 identical manifests, sha256 {key[:16]}")
