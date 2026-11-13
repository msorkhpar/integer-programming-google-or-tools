"""Lesson 10.2.4: canonical bytes, digests and the versions a run manifest records.

A run manifest is the record of one solve that a rerun is compared with: what went in (the input
snapshot's digest and the model's options), which solver and parameters ran it, which versions of
the software, and what came out (status, objective, bound, the plan and its digest, the work done).
Wall time stays out: it is a fact about the machine, not about the run. So does anything that names
the machine or a person (host name, user name, home path); a manifest is shared and archived.
"""

from __future__ import annotations

import hashlib
import json
import platform
from importlib.metadata import version


def canonical(obj) -> bytes:
    """One byte string per value: sorted keys, no spaces, ASCII only."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def versions(solver: str) -> dict:
    """The software a run depended on. OR-Tools' wheel carries its own HiGHS and SCIP libraries."""
    found = {"python": platform.python_version(), "ortools": version("ortools"),
             "platform": f"{platform.system()}-{platform.machine()}"}
    if solver == "gurobi":
        found["gurobipy"] = version("gurobipy")
    return found


def volatile_free(record: dict) -> dict:
    """The manifest of a run record: everything but its clock readings."""
    return record["manifest"]


def show(manifest: dict) -> None:
    """Print a manifest one field per line, the plan cut to its first three starts."""
    for section in sorted(manifest):
        for key in sorted(manifest[section]):
            value = manifest[section][key]
            if section == "result" and key == "plan":
                text = json.dumps(value[:3], separators=(",", ":"))[:-1] + f",...]  ({len(value)} starts)"
            else:
                text = json.dumps(value, sort_keys=True, separators=(",", ":"))
            print(f"{section + '.' + key:<20} {text}")


if __name__ == "__main__":
    from solve_once import run

    config = {"size": "small", "objective": "npv", "order": "given", "solver": "highs",
              "params": {"relative_gap_tolerance": 0.0}}
    first, second = run(config), run(config)
    show(first["manifest"])
    print("manifest sha256 ", sha256(first["manifest"])[:16], "| second run", sha256(second["manifest"])[:16])
    print("same bytes:", canonical(first["manifest"]) == canonical(second["manifest"]))
    print("kept out of the manifest:", sorted(first["clock"]))
