"""A determinism test: solve each golden scenario in fresh processes and compare the bytes.

This is the idea of lesson 10.2.5's run harness cut down to what a test suite needs: each run is a
new Python process with its own PYTHONHASHSEED, it prints its result as canonical JSON, and the
parent compares the digests. GridCap is a fictional utility's portfolio.

    python3 determinism.py                       # every scenario, model built in id order
    python3 determinism.py --child NAME ORDER    # one run (what the parent starts)
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent


def child(name: str, order: str) -> None:
    from golden import result, scenarios
    portfolio = scenarios()[name]
    if order == "set":
        # The known bug: rows read in the order a set of ids happens to iterate in.
        ids = {p.project_id for p in portfolio.projects}
        portfolio = replace(portfolio, projects=tuple(portfolio.project(pid) for pid in ids))
    print(json.dumps(result(portfolio), sort_keys=True, separators=(",", ":")))


def digests(name: str, order: str = "id", runs: int = 5) -> list[str]:
    """The sha256 of each run's output, each run a fresh process with its own hash seed."""
    path = os.pathsep.join([str(HERE.parents[1] / "00-base"), str(HERE)])
    found = []
    for seed in range(1, runs + 1):
        env = {**os.environ, "PYTHONHASHSEED": str(seed), "PYTHONPATH": path}
        out = subprocess.run([sys.executable, str(HERE / "determinism.py"), "--child", name, order],
                             env=env, capture_output=True, text=True, check=True).stdout
        found.append(hashlib.sha256(out.encode("utf-8")).hexdigest()[:12])
    return found


def main() -> None:
    from golden import scenarios
    for name in scenarios():
        runs = digests(name)
        verdict = "same bytes" if len(set(runs)) == 1 else "DIFFERENT"
        print(f"{name:<34} 5 processes: {verdict}  {runs[0]}")
    runs = digests("two equal projects, room for one", order="set")
    print(f"{'the tie, rows in set order':<34} 5 processes: {len(set(runs))} different outputs  {' '.join(runs)}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--child"]:
        child(sys.argv[2], sys.argv[3])
    else:
        main()
