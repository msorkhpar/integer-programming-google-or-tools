"""CIPT Lite, milestone 1: load a portfolio export, validate it, and snapshot it under its content hash.

GridCap is a fictional utility's portfolio, generated for this course; none of its numbers are real.

Three stages, in the order lesson 12.2.3's design note fixes:

1. `read_export(folder)` reads the five CSV files and `portfolio.json` that `gridcap.save_csv`
   writes. Every cell is checked as it is read (types, known codes, windows, references), every
   problem is kept, and a `Portfolio` is built only when there is none (lessons 1.3.2 and 12.2.1).
2. `gate(portfolio)` runs the rules that look across projects: parent cycles, children whose parent
   cannot start early enough, must-dos with no start, and money every plan must spend in a year
   above that year's budget (lesson 12.2.2). Errors block; warnings are reported.
3. `canonical(portfolio)` writes the validated content one way, and `digest` is its SHA-256
   (lessons 10.2.4 and 12.2.3). `SnapshotStore` keeps each snapshot once under its digest and
   re-hashes it on every read.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from gridcap import PROGRAMS, REGIONS, Asset, Portfolio, Project

Severity = Literal["error", "warning"]
FLOAT_PLACES = 6


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: Severity
    subject: str
    detail: str


class Rejected(Exception):
    """The export cannot be snapshotted; `findings` says why, every problem at once."""

    def __init__(self, findings: list[Finding]):
        super().__init__(f"{sum(f.severity == 'error' for f in findings)} error(s)")
        self.findings = findings


# ---------------------------------------------------------------------------------------------
# 1. Read every cell, keep every problem


class Cells:
    """Converts one CSV row's cells, recording a finding instead of raising."""

    def __init__(self, found: list[Finding], subject: str):
        self.found, self.subject = found, subject

    def whole(self, row: dict, column: str, low: int = 0) -> int:
        text = row.get(column, "")
        try:
            value = int(text)
        except ValueError:
            self.found.append(Finding("not-a-whole-number", "error", self.subject, f"{column} = {text!r}"))
            return low
        if value < low:
            self.found.append(Finding("below-minimum", "error", self.subject, f"{column} = {value} < {low}"))
        return value

    def number(self, row: dict, column: str, low: float, high: float) -> float:
        text = row.get(column, "")
        try:
            value = float(text)
        except ValueError:
            value = math.nan
        if not math.isfinite(value) or not low < value <= high:
            self.found.append(Finding("out-of-range", "error", self.subject, f"{column} = {text!r}"))
            return high
        return value

    def code(self, row: dict, column: str, allowed: tuple[str, ...]) -> str:
        text = row.get(column, "")
        if text not in allowed:
            self.found.append(Finding("unknown-code", "error", self.subject, f"{column} = {text!r}"))
        return text


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_export(folder: str | Path) -> tuple[Portfolio | None, list[Finding]]:
    """The portfolio in `folder`, or None, and every problem found in its cells."""
    src = Path(folder)
    found: list[Finding] = []
    scalars = json.loads((src / "portfolio.json").read_text(encoding="utf-8"))
    years = tuple(scalars["years"])

    npv: dict[str, dict[int, int]] = {}
    for row in _rows(src / "npv.csv"):
        cells = Cells(found, row.get("project_id", "?"))
        npv.setdefault(row["project_id"], {})[cells.whole(row, "start_year")] = cells.whole(row, "npv", low=-10**9)

    assets = []
    for row in _rows(src / "assets.csv"):
        c = Cells(found, row.get("asset_id", "?"))
        assets.append(Asset(asset_id=row["asset_id"], kind=row["kind"], region=c.code(row, "region", REGIONS),
                            age=c.whole(row, "age"), weibull_beta=c.number(row, "weibull_beta", 0, 20),
                            weibull_eta=c.number(row, "weibull_eta", 0, 500), rul=c.whole(row, "rul", low=1),
                            cof=c.whole(row, "cof")))
    asset_ids = {a.asset_id for a in assets}

    projects, seen = [], set()
    for row in _rows(src / "projects.csv"):
        pid = row.get("project_id", "?")
        c = Cells(found, pid)
        if pid in seen:
            found.append(Finding("duplicate-id", "error", pid, "two rows share this project id"))
        seen.add(pid)
        profile = [c.whole({"cost": text}, "cost") for text in row.get("cost_profile", "").split(";")]
        first, last = c.whole(row, "earliest_start"), c.whole(row, "latest_start")
        if not (years[0] <= first <= last and last + len(profile) - 1 <= years[-1]):
            found.append(Finding("empty-window", "error", pid,
                                 f"starts {first}-{last} with {len(profile)} year(s) of work in {years[0]}-{years[-1]}"))
        if row.get("asset_id") not in asset_ids:
            found.append(Finding("unknown-asset", "error", pid, f"asset_id = {row.get('asset_id')!r}"))
        values = npv.get(pid, {})
        missing = [t for t in range(first, last + 1) if t not in values]
        if missing and first <= last:
            found.append(Finding("npv-missing", "error", pid, f"no NPV for start(s) {missing}"))
        projects.append(Project(
            project_id=pid, name=row.get("name", ""), program=c.code(row, "program", PROGRAMS),
            region=c.code(row, "region", REGIONS), asset_id=row.get("asset_id", ""),
            intervention=row.get("intervention", ""), cost_profile=tuple(profile),
            earliest_start=first, latest_start=last, must_do=c.code(row, "must_do", ("0", "1")) == "1",
            parent=row.get("parent") or None, parent_lag=c.whole(row, "parent_lag"),
            alt_group=row.get("alt_group") or None, crew_months=c.whole(row, "crew_months", low=1),
            npv={t: v for t, v in sorted(values.items())}))
    for p in projects:
        if p.parent and p.parent not in seen:
            found.append(Finding("unknown-parent", "error", p.project_id, f"parent = {p.parent!r}"))

    budget, region_budget, floor = {}, {}, {}
    for row in _rows(src / "budgets.csv"):
        c = Cells(found, f"budget {row.get('region')} {row.get('year')}")
        year, amount = c.whole(row, "year"), c.whole(row, "budget")
        if row["region"] == "ALL":
            budget[year] = amount
        elif year == 0:
            floor[c.code(row, "region", REGIONS)] = amount
        else:
            region_budget[(c.code(row, "region", REGIONS), year)] = amount
    crews = {}
    for row in _rows(src / "crews.csv"):
        c = Cells(found, f"crews {row.get('program')} {row.get('year')}")
        crews[(c.code(row, "program", PROGRAMS), c.whole(row, "year"))] = c.whole(row, "crew_months")
    for y in years:
        if y not in budget:
            found.append(Finding("missing-budget", "error", str(y), "no ALL budget row for this year"))

    if any(f.severity == "error" for f in found):
        return None, found
    return Portfolio(name=scalars["name"], seed=scalars["seed"], years=years,
                     discount_rate=scalars["discount_rate"], projects=tuple(projects), assets=tuple(assets),
                     capital_budget=scalars["capital_budget"], budget=budget, region_budget=region_budget,
                     region_floor=floor, crews=crews), found


# ---------------------------------------------------------------------------------------------
# 2. Rules across projects


def parent_cycle(pf: Portfolio) -> list[Finding]:
    parent = {p.project_id: p.parent for p in pf.projects}
    found, seen = [], set()
    for start in sorted(parent):
        path, pid = [], start
        while pid is not None and pid not in path:
            path.append(pid)
            pid = parent.get(pid)
        if pid is not None:
            loop = path[path.index(pid):]
            if frozenset(loop) not in seen:
                seen.add(frozenset(loop))
                found.append(Finding("parent-cycle", "error", " -> ".join(loop + [pid]),
                                     "a project cannot be its own ancestor"))
    return found


def parent_too_late(pf: Portfolio) -> list[Finding]:
    """A child none of whose starts its parent can reach, lag included: an error for a must-do."""
    by_id = {p.project_id: p for p in pf.projects}
    found = []
    for c in pf.projects:
        if c.parent and by_id[c.parent].earliest_start + c.parent_lag > c.latest_start:
            found.append(Finding("parent-too-late", "error" if c.must_do else "warning", c.project_id,
                                 f"{c.parent} starts {by_id[c.parent].earliest_start} at the earliest, "
                                 f"lag {c.parent_lag}; {c.project_id} starts {c.latest_start} at the latest"))
    return found


def must_spend_over_budget(pf: Portfolio) -> list[Finding]:
    """Each year: the least that must-do work must spend there, against the year's budget."""
    found = []
    for y in pf.years:
        least = sum(min(p.spend(t).get(y, 0) for t in p.starts()) for p in pf.projects if p.must_do)
        if least > pf.budget[y]:
            found.append(Finding("must-spend-over-budget", "error", str(y),
                                 f"must-do work spends at least ${least:,}k; the budget is ${pf.budget[y]:,}k"))
    return found


def alternative_mandates(pf: Portfolio) -> list[Finding]:
    groups: dict[str, list[str]] = {}
    for p in pf.projects:
        if p.alt_group and p.must_do:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    return [Finding("two-must-do-alternatives", "error", g, f"{', '.join(m)} are all must-do")
            for g, m in sorted(groups.items()) if len(m) > 1]


RULES = [parent_cycle, parent_too_late, must_spend_over_budget, alternative_mandates]


def gate(pf: Portfolio) -> list[Finding]:
    found = [f for rule in RULES for f in rule(pf)]
    return sorted(found, key=lambda f: (f.severity != "error", f.rule, f.subject))


def blocked(findings: list[Finding]) -> bool:
    return any(f.severity == "error" for f in findings)


# ---------------------------------------------------------------------------------------------
# 3. Canonical bytes, digest, store


def fixed(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{value} has no canonical form")
    return float(f"{value:.{FLOAT_PLACES}f}") + 0.0


def _normal(value):
    if isinstance(value, float):
        return fixed(value)
    if isinstance(value, dict):
        return {k: _normal(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normal(v) for v in value]
    return value


def canonical(pf: Portfolio) -> bytes:
    """Validated content, one way: records sorted by id, keys sorted, floats fixed, no spaces."""
    tree = pf.to_dict()
    tree["projects"].sort(key=lambda p: p["project_id"])
    tree["assets"].sort(key=lambda a: a["asset_id"])
    return json.dumps(_normal(tree), sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def digest(pf: Portfolio) -> str:
    return hashlib.sha256(canonical(pf)).hexdigest()


def snapshot(folder: str | Path) -> tuple[Portfolio, str, list[Finding]]:
    """Read, validate and hash an export: (portfolio, digest, warnings), or raise Rejected."""
    pf, found = read_export(folder)
    if pf is None:
        raise Rejected(found)
    found += gate(pf)
    if blocked(found):
        raise Rejected(found)
    return pf, digest(pf), found


class Corrupted(Exception):
    pass


class SnapshotStore:
    """Snapshots on disk, each stored once as `<digest>.json` and re-hashed on every read."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, pf: Portfolio) -> str:
        data = canonical(pf)
        key = hashlib.sha256(data).hexdigest()
        path = self.root / f"{key}.json"
        if not path.exists():
            path.write_bytes(data)
        return key

    def get(self, key: str) -> Portfolio:
        data = (self.root / f"{key}.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != key:
            raise Corrupted(f"{key[:12]}.json no longer hashes to its name")
        return Portfolio.from_dict(json.loads(data))
