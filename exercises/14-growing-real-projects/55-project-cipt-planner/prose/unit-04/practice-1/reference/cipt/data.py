"""The planning export, read into typed records.

The planners' export carries every column the planning system keeps (cost profiles, windows,
rules, NPV by start year, asset health). This version reads only the columns it uses and ignores
the rest, so the same export file serves every version of the planner.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Asset:
    """The equipment a project works on: its age now, its Weibull curve and what a failure costs."""

    asset_id: str
    age: int                        # years, at the start of the plan's first year
    weibull_beta: float             # shape
    weibull_eta: float              # scale, years
    cof: int                        # $k, the consequence of one failure


@dataclass(frozen=True)
class Project:
    """One candidate project, as this version of the planner sees it."""

    project_id: str
    name: str
    cost_profile: tuple[int, ...]   # $k spent in each year of work, from the start year on
    npv: dict[int, int]             # $k, the NPV finance quotes for each start year
    asset: Asset
    earliest_start: int
    latest_start: int
    must_do: bool = False
    parent: str | None = None       # a project that must have started `parent_lag` years before
    parent_lag: int = 0
    alt_group: str | None = None    # at most one project of a group is funded
    bundle: str | None = None       # every project of a bundle is funded, or none

    @property
    def value(self) -> int:
        """The NPV of a start in the earliest year: what the planner used before lesson 14.2.4."""
        return self.npv[self.earliest_start]

    @property
    def capex(self) -> int:
        return sum(self.cost_profile)

    @property
    def duration(self) -> int:
        return len(self.cost_profile)

    def spend(self, start: int) -> dict[int, int]:
        """What the project spends in each calendar year if it starts in `start`."""
        return {start + k: amount for k, amount in enumerate(self.cost_profile)}


@dataclass(frozen=True)
class Request:
    """What the planners ask for: the projects, the years, and each year's budget."""

    name: str
    years: tuple[int, ...]
    budget: dict[int, int]          # $k available in each year
    projects: tuple[Project, ...]
    objective: str = "npv"          # "npv" or "risk": what the plan maximizes

    def project(self, project_id: str) -> Project:
        for p in self.projects:
            if p.project_id == project_id:
                return p
        raise KeyError(project_id)

    def groups(self, column: str) -> dict[str, list[str]]:
        """Projects sharing a value of `column` ("alt_group" or "bundle"), by that value, in id order."""
        found: dict[str, list[str]] = {}
        for p in self.projects:
            if getattr(p, column) is not None:
                found.setdefault(getattr(p, column), []).append(p.project_id)
        return {g: sorted(members) for g, members in sorted(found.items())}

    def starts(self, project: Project) -> range:
        """The project's window, cut so that its work starts and ends inside the plan's years."""
        first = max(project.earliest_start, self.years[0])
        last = min(project.latest_start, self.years[-1] - project.duration + 1)
        return range(first, last + 1)


def load_request(raw: dict) -> Request:
    """Build a Request from the export's dictionary form, refusing duplicate project ids."""
    projects = tuple(
        Project(
            project_id=row["id"],
            name=row["name"],
            cost_profile=tuple(row["cost_profile"]),
            npv={int(t): v for t, v in row["npv"].items()},
            asset=Asset(row["asset"]["id"], row["asset"]["age"], row["asset"]["weibull_beta"],
                        row["asset"]["weibull_eta"], row["asset"]["cof"]),
            earliest_start=row["earliest_start"],
            latest_start=row["latest_start"],
            must_do=row["must_do"],
            parent=row["parent"],
            parent_lag=row["parent_lag"],
            alt_group=row["alt_group"],
            bundle=row["bundle"],
        )
        for row in raw["projects"]
    )
    ids = [p.project_id for p in projects]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate project ids in the export")
    for p in projects:
        if p.parent is not None and p.parent not in ids:
            raise ValueError(f"{p.project_id} names an unknown parent {p.parent}")
    objective = raw.get("objective", "npv")
    if objective not in ("npv", "risk"):
        raise ValueError(f"unknown objective {objective!r}")
    return Request(name=raw["name"], years=tuple(raw["years"]),
                   budget={int(y): v for y, v in raw["budget"].items()}, projects=projects,
                   objective=objective)


def read_request(path: str | Path) -> Request:
    """Read an export file (JSON) into a Request."""
    return load_request(json.loads(Path(path).read_text(encoding="utf-8")))
