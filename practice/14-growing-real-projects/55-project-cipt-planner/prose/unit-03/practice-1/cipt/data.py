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
class Project:
    """One candidate project, as this version of the planner sees it."""

    project_id: str
    name: str
    cost_profile: tuple[int, ...]   # $k spent in each year of work, from the start year on
    value: int                      # $k, the NPV finance quotes for a start in the earliest year
    earliest_start: int
    latest_start: int

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

    def project(self, project_id: str) -> Project:
        for p in self.projects:
            if p.project_id == project_id:
                return p
        raise KeyError(project_id)

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
            value=row["npv"][str(row["earliest_start"])],
            earliest_start=row["earliest_start"],
            latest_start=row["latest_start"],
        )
        for row in raw["projects"]
    )
    ids = [p.project_id for p in projects]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate project ids in the export")
    return Request(name=raw["name"], years=tuple(raw["years"]),
                   budget={int(y): v for y, v in raw["budget"].items()}, projects=projects)


def read_request(path: str | Path) -> Request:
    """Read an export file (JSON) into a Request."""
    return load_request(json.loads(Path(path).read_text(encoding="utf-8")))
