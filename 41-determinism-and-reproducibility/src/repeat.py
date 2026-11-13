"""Run one config several times, each in a fresh Python process, and report what repeated.

Each run gets its own process and its own hash seed (PYTHONHASHSEED = 1, 2, 3, ...), so anything in
the model-building code that depends on a set's order shows up as a difference (lesson 10.2.1), and
HiGHS's thread count, fixed per process (lesson 4.2.4), is set afresh by every run.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import gridcap

HERE = Path(__file__).resolve().parent
PATH = os.pathsep.join([str(HERE), str(Path(gridcap.__file__).resolve().parents[1])])


def child_env(seed: str) -> dict:
    """The environment of a child run: its own hash seed, and this module and GridCap importable."""
    return {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": PATH}


def repeat(config: dict, runs: int) -> list[dict]:
    """The run records of `runs` fresh processes solving `config`."""
    records = []
    for k in range(runs):
        env = child_env(str(k + 1))
        done = subprocess.run([sys.executable, str(HERE / "solve_once.py"), json.dumps(config)],
                              env=env, capture_output=True, text=True, check=True)
        records.append(json.loads(done.stdout))
    return records


def field(record: dict, path: str):
    """record["manifest"]["result"]["status"] for the path "result.status" (or "clock.wall_seconds")."""
    node = record if path.startswith("clock") else record["manifest"]
    for part in path.split("."):
        node = node[part]
    return node


def shown(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return f"{value:,.0f}"
    if isinstance(value, float):
        return f"{value:,.4f}"
    return f"{value:,}" if isinstance(value, int) else str(value)


def summary(label: str, records: list[dict], paths: list[str]) -> None:
    """One line per field: its value if every run gave the same one, `differs` if not."""
    print(f"{label} ({len(records)} runs)")
    for path in paths:
        values = {json.dumps(field(r, path), sort_keys=True) for r in records}
        print(f"  {path:<34} {shown(field(records[0], path)) if len(values) == 1 else 'differs'}")
