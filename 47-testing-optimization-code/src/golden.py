"""A golden dataset for the planning model: fixed scenarios, their stored results, and a comparison.

GridCap is a fictional utility's portfolio. The golden file `golden/plan_results.json` holds, for
each scenario, the input's content hash and the result a reviewed version of the model produced.
`compare` checks a new result against it field by field, within stated tolerances, and returns one
line per difference.

    python3 golden.py            # compare the current model with the golden file
    python3 golden.py --update   # rewrite the golden file (review the diff before committing it)
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

from gridcap import Portfolio, generate

from audit import spend_by_year
from plan_model import optimize
from tiny import portfolio, project

GOLDEN = Path(__file__).resolve().parent / "golden" / "plan_results.json"

#: What "the same" means, field by field. Money is in $k.
TOLERANCE = {"objective": 0.01}     # $10: far above solver noise (1e-5), far below one project


def scenarios() -> dict[str, Portfolio]:
    """The golden scenarios: small enough to solve in a second, each with something that binds."""
    small = generate("small")
    cut = {y: (b * 8 // 10 if y == 2028 else b) for y, b in small.budget.items()}
    tie = portfolio(project("A", (50,), (2027, 2027), npv=30), project("B", (50,), (2027, 2027), npv=30),
                    budget={2027: 60}, name="tie")
    return {"tiny": generate("tiny"), "small": small,
            "small, 2028 budget cut 20%": replace(small, budget=cut),
            "two equal projects, room for one": tie}


def input_hash(portfolio: Portfolio) -> str:
    """sha256 of the canonical JSON with projects in id order: the same data in any row order."""
    data = portfolio.to_dict()
    data["projects"].sort(key=lambda p: p["project_id"])
    text = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def result(portfolio: Portfolio, rules: dict | None = None) -> dict:
    """What a golden record holds: the input's identity and the solve's status, value, plan and spend."""
    status, npv, plan = optimize(portfolio, rules)
    return {"input_sha256": input_hash(portfolio), "status": status,
            "objective": round(npv, 3), "plan": plan,
            "spend": {str(y): v for y, v in spend_by_year(portfolio, plan).items()}}


def compare(expected: dict, actual: dict, tolerance: dict = TOLERANCE) -> list[str]:
    """Every difference between a golden record and a new one, most fundamental first."""
    if expected["input_sha256"] != actual["input_sha256"]:
        return [f"input changed: sha256 {expected['input_sha256']} -> {actual['input_sha256']} "
                "(the data moved, not the model: regenerate this record on purpose)"]
    if expected["status"] != actual["status"]:
        return [f"status: {expected['status']} -> {actual['status']}"]
    lines = []
    delta = actual["objective"] - expected["objective"]
    if abs(delta) > tolerance["objective"]:
        lines.append(f"objective: {expected['objective']:,.3f} -> {actual['objective']:,.3f} "
                     f"({delta:+,.3f}, tolerance {tolerance['objective']})")
    was, now = expected["plan"], actual["plan"]
    for pid in sorted(set(was) | set(now)):
        if pid not in now:
            lines.append(f"plan: {pid} dropped (was {was[pid]})")
        elif pid not in was:
            lines.append(f"plan: {pid} added (starts {now[pid]})")
        elif was[pid] != now[pid]:
            lines.append(f"plan: {pid} moved {was[pid]} -> {now[pid]}")
    for year in expected["spend"]:
        if expected["spend"][year] != actual["spend"][year]:
            lines.append(f"spend {year}: {expected['spend'][year]:,} -> {actual['spend'][year]:,}")
    if lines and abs(delta) <= tolerance["objective"]:
        lines.append("same value, another plan: a tie picked differently")
    return lines


def load() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def write(records: dict) -> None:
    GOLDEN.parent.mkdir(exist_ok=True)
    GOLDEN.write_text(json.dumps(records, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    current = {name: result(p) for name, p in scenarios().items()}
    if "--update" in sys.argv:
        write(current)
        print(f"wrote {len(current)} records to {GOLDEN.name}; review the diff before committing")
        return
    golden = load()
    for name, record in current.items():
        found = compare(golden[name], record)
        count = len(record["plan"])
        print(f"{'PASS' if not found else 'FAIL'} {name}: {record['status']}, NPV {record['objective']:,.1f}, "
              f"{count} project{'' if count == 1 else 's'}")
        for line in found:
            print("     " + line)


if __name__ == "__main__":
    main()
