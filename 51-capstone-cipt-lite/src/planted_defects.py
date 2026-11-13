"""Lesson 13.1.1: GridCap medium's export with six planted defects, each refused with its reason.

Each defect is a mistake a planning export really makes (a typed number, a misspelt code, a stale
id, a typo in a budget). The program plants them one at a time, then all six together, and runs the
milestone's `snapshot`. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from cipt_data import Rejected, snapshot
from gridcap import generate, save_csv


def edit(folder: Path, file: str, key: tuple[str, str], column: str, value: str) -> None:
    """Set one cell: the row whose `key[0]` column equals `key[1]`."""
    path = folder / file
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
        names = list(rows[0])
    hits = [r for r in rows if r[key[0]] == key[1]]
    assert hits, f"no row {key} in {file}"
    for r in hits:
        r[column] = value
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)


DEFECTS = {
    "P010 cost typed with a comma": ("projects.csv", ("project_id", "P010"), "cost_profile", "1,200"),
    "P020 region misspelt": ("projects.csv", ("project_id", "P020"), "region", "Vally"),
    "P030 window reversed": ("projects.csv", ("project_id", "P030"), "earliest_start", "2036"),
    "P040 parent retired": ("projects.csv", ("project_id", "P040"), "parent", "P999"),
    "P050 and P051 each other's parent": None,
    "2029 budget typed 391": ("budgets.csv", ("region", "ALL"), "budget", None),
}


def plant(folder: Path, name: str) -> None:
    if name == "P050 and P051 each other's parent":
        edit(folder, "projects.csv", ("project_id", "P050"), "parent", "P051")
        edit(folder, "projects.csv", ("project_id", "P051"), "parent", "P050")
    elif name == "2029 budget typed 391":
        path = folder / "budgets.csv"
        text = path.read_text(encoding="utf-8").replace("2029,ALL,39190", "2029,ALL,391")
        path.write_text(text, encoding="utf-8")
    else:
        file, key, column, value = DEFECTS[name]
        edit(folder, file, key, column, value)


def attempt(names: list[str]) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        folder = save_csv(generate("medium"), Path(tmp) / "export")
        for name in names:
            plant(folder, name)
        try:
            _, key, _ = snapshot(folder)
            return [f"accepted {key[:12]}"]
        except Rejected as no:
            return [f"{f.rule:<23} {f.subject:<14} {f.detail}" for f in no.findings if f.severity == "error"]


if __name__ == "__main__":
    for name in DEFECTS:
        lines = attempt([name])
        print(f"{name:<36} -> {lines[0]}")
        for extra in lines[1:]:
            print(f"{'':<36}    {extra}")
    print()
    every = attempt(list(DEFECTS))
    print(f"all six planted at once: refused with {len(every)} errors")
    for line in every:
        print("  ", line)
