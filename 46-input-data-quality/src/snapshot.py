"""Lesson 12.2.1: the schema of a GridCap input snapshot, and the planning export that writes one.

A snapshot is one JSON document holding everything the planning model reads: the years, the
budgets, the crews, the regional floors and the candidate projects. The planning database exports
it, and the optimization service validates it against `Snapshot` before anything else touches it.
GridCap is a fictional utility; its numbers describe no real company.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, model_validator

from gridcap import Portfolio

SCHEMA_VERSION = 1
Program = Literal["transmission", "distribution", "vegetation"]
Region = Literal["Ridge", "Valley", "Coast", "Plains"]


class Contract(BaseModel):
    """Every part of a snapshot: no unknown keys, no guessed conversions, no edits after loading."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class ProjectIn(Contract):
    project_id: str = Field(pattern=r"^P\d{3}$")
    program: Program
    region: Region
    cost_profile: tuple[NonNegativeInt, ...] = Field(min_length=1)    # $k per year of work
    earliest_start: int
    latest_start: int
    must_do: bool
    parent: str | None = None
    parent_lag: NonNegativeInt = 0                                     # years after the parent starts
    alt_group: str | None = None
    crew_months: NonNegativeInt                                        # per year of work
    npv: tuple[int, ...]                                               # $k, one per start year in the window

    @model_validator(mode="after")
    def window_and_npv_agree(self):
        if self.earliest_start > self.latest_start:
            raise ValueError("earliest_start is after latest_start")
        if len(self.npv) != self.latest_start - self.earliest_start + 1:
            raise ValueError("npv needs one value per start year of the window")
        return self


class YearAmount(Contract):
    year: int
    amount: NonNegativeInt                                             # $k


class CrewLimit(Contract):
    program: Program
    year: int
    crew_months: NonNegativeInt


class RegionFloor(Contract):
    region: Region
    amount: NonNegativeInt                                             # $k over the whole plan


class Snapshot(Contract):
    schema_version: Literal[1]
    name: str
    years: tuple[int, ...] = Field(min_length=1)
    discount_rate: float = Field(gt=0, lt=1)
    budget: tuple[YearAmount, ...]
    crews: tuple[CrewLimit, ...]
    region_floor: tuple[RegionFloor, ...]
    projects: tuple[ProjectIn, ...]

    @model_validator(mode="after")
    def references_resolve(self):
        """Every id and key the model will look up exists, exactly once. All problems at once."""
        problems = []
        ids = Counter(p.project_id for p in self.projects)
        problems += [f"project {pid} appears {n} times" for pid, n in sorted(ids.items()) if n > 1]
        problems += [f"{p.project_id}: parent {p.parent} is not a project"
                     for p in self.projects if p.parent and p.parent not in ids]
        years = Counter(b.year for b in self.budget)
        problems += [f"year {y}: {years[y]} budget rows" for y in self.years if years[y] != 1]
        crews = Counter((c.program, c.year) for c in self.crews)
        problems += [f"{q} {y}: {crews[q, y]} crew rows" for q in Program.__args__ for y in self.years
                     if crews[q, y] != 1]
        if problems:
            raise ValueError("; ".join(problems))
        return self


def export(portfolio: Portfolio) -> dict:
    """The planning database's export of a GridCap portfolio: a JSON-ready snapshot document."""
    return {
        "schema_version": SCHEMA_VERSION,
        "name": portfolio.name,
        "years": list(portfolio.years),
        "discount_rate": portfolio.discount_rate,
        "budget": [{"year": y, "amount": v} for y, v in portfolio.budget.items()],
        "crews": [{"program": q, "year": y, "crew_months": v} for (q, y), v in portfolio.crews.items()],
        "region_floor": [{"region": r, "amount": v} for r, v in portfolio.region_floor.items()],
        "projects": [
            {"project_id": p.project_id, "program": p.program, "region": p.region,
             "cost_profile": list(p.cost_profile), "earliest_start": p.earliest_start,
             "latest_start": p.latest_start, "must_do": p.must_do, "parent": p.parent,
             "parent_lag": p.parent_lag, "alt_group": p.alt_group, "crew_months": p.crew_months,
             "npv": [p.npv[t] for t in p.starts()]}
            for p in portfolio.projects
        ],
    }


def load(text: str | bytes) -> Snapshot:
    """Validate a snapshot document as it arrives over the wire: JSON text in, a Snapshot out."""
    return Snapshot.model_validate_json(text)


def project(doc: dict, pid: str) -> dict:
    """The record of project `pid` in a snapshot document (a dict, so a program can plant an error)."""
    return next(p for p in doc["projects"] if p["project_id"] == pid)


def as_json(doc: dict) -> str:
    return json.dumps(doc)
