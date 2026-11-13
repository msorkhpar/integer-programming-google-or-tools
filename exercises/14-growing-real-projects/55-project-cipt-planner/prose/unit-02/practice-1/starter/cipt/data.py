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
    capex: int            # $k, the whole cost over the project's life
    value: int            # $k, the NPV finance quotes for a start in the earliest year
    earliest_start: int


@dataclass(frozen=True)
class Request:
    """What the planners ask for: the projects, and the money to fund them with."""

    name: str
    capital_budget: int   # $k, one envelope for the whole plan
    projects: tuple[Project, ...]

    def project(self, project_id: str) -> Project:
        for p in self.projects:
            if p.project_id == project_id:
                return p
        raise KeyError(project_id)

    def starts(self, project: Project) -> range:
        """The years the project may start in. Stub: lesson 14.2.2 writes the window; until then,
        the earliest year alone, the year this version assumes."""
        return range(project.earliest_start, project.earliest_start + 1)


def load_request(raw: dict) -> Request:
    """Build a Request from the export's dictionary form, refusing duplicate project ids."""
    projects = tuple(
        Project(
            project_id=row["id"],
            name=row["name"],
            capex=sum(row["cost_profile"]),
            value=row["npv"][str(row["earliest_start"])],
            earliest_start=row["earliest_start"],
        )
        for row in raw["projects"]
    )
    ids = [p.project_id for p in projects]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate project ids in the export")
    return Request(name=raw["name"], capital_budget=raw["capital_budget"], projects=projects)


def read_request(path: str | Path) -> Request:
    """Read an export file (JSON) into a Request."""
    return load_request(json.loads(Path(path).read_text(encoding="utf-8")))
