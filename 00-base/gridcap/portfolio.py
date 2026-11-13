"""The GridCap data model: projects, assets and limits of a fictional utility's capital portfolio.

GridCap is invented for this course. No number in it describes a real utility.

Money is in thousands of dollars ($k) and stored as integers, so sums are exact and a plan's cost
never depends on float rounding. Years are calendar years.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Mapping

PROGRAMS = ("transmission", "distribution", "vegetation")
REGIONS = ("Ridge", "Valley", "Coast", "Plains")


@dataclass(frozen=True)
class Asset:
    """One piece of equipment a project works on.

    `weibull_beta` (shape) and `weibull_eta` (scale, in years) give its probability-of-failure
    curve; `rul` is the remaining useful life, in years, that an asset-health model predicted;
    `cof` is the consequence of one failure, in $k.
    """

    asset_id: str
    kind: str
    region: str
    age: int
    weibull_beta: float
    weibull_eta: float
    rul: int
    cof: int


@dataclass(frozen=True)
class Project:
    """One candidate capital project.

    `cost_profile[k]` is what the project spends in its k-th year of work, so a project started in
    year s spends `cost_profile[k]` in year s + k. `npv[s]` is its net present value, in $k, if it
    starts in year s; only years between `earliest_start` and `latest_start` are keys.
    """

    project_id: str
    name: str
    program: str
    region: str
    asset_id: str
    intervention: str
    cost_profile: tuple[int, ...]
    earliest_start: int
    latest_start: int
    must_do: bool
    parent: str | None
    parent_lag: int
    alt_group: str | None
    crew_months: int
    npv: Mapping[int, int] = field(default_factory=dict)

    @property
    def capex(self) -> int:
        """Total cost over the project's life, in $k."""
        return sum(self.cost_profile)

    @property
    def duration(self) -> int:
        """Years of work."""
        return len(self.cost_profile)

    @property
    def value(self) -> int:
        """The project's NPV if it starts as early as it can, in $k."""
        return self.npv[self.earliest_start]

    def starts(self) -> range:
        """Every year the project may start in."""
        return range(self.earliest_start, self.latest_start + 1)

    def spend(self, start: int) -> dict[int, int]:
        """What the project spends in each calendar year if it starts in `start`."""
        if start not in self.starts():
            raise ValueError(f"{self.project_id} cannot start in {start}")
        return {start + k: amount for k, amount in enumerate(self.cost_profile)}


@dataclass(frozen=True)
class Portfolio:
    """A whole GridCap instance: its projects, assets and limits.

    `capital_budget` is the single budget the one-period models of sections 1–3 use. The
    multi-period models use `budget[year]` (all regions) and `region_budget[(region, year)]`,
    `crews[(program, year)]` (crew-months available) and `region_floor[region]` (the least a
    region must receive over the horizon, a rate-case commitment).
    """

    name: str
    seed: int
    years: tuple[int, ...]
    discount_rate: float
    projects: tuple[Project, ...]
    assets: tuple[Asset, ...]
    capital_budget: int
    budget: Mapping[int, int]
    region_budget: Mapping[tuple[str, int], int]
    region_floor: Mapping[str, int]
    crews: Mapping[tuple[str, int], int]

    def project(self, project_id: str) -> Project:
        for project in self.projects:
            if project.project_id == project_id:
                return project
        raise KeyError(project_id)

    def asset(self, asset_id: str) -> Asset:
        for asset in self.assets:
            if asset.asset_id == asset_id:
                return asset
        raise KeyError(asset_id)

    @property
    def project_ids(self) -> tuple[str, ...]:
        return tuple(p.project_id for p in self.projects)

    def to_dict(self) -> dict:
        """A JSON-ready form. Tuple keys become `"a|b"` strings and int keys become strings."""
        return {
            "name": self.name,
            "seed": self.seed,
            "years": list(self.years),
            "discount_rate": self.discount_rate,
            "capital_budget": self.capital_budget,
            "budget": {str(y): v for y, v in self.budget.items()},
            "region_budget": {f"{r}|{y}": v for (r, y), v in self.region_budget.items()},
            "region_floor": dict(self.region_floor),
            "crews": {f"{p}|{y}": v for (p, y), v in self.crews.items()},
            "assets": [asdict(a) for a in self.assets],
            "projects": [
                {**asdict(p), "cost_profile": list(p.cost_profile),
                 "npv": {str(y): v for y, v in p.npv.items()}}
                for p in self.projects
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        def pair(key: str) -> tuple[str, int]:
            a, b = key.split("|")
            return a, int(b)

        return cls(
            name=data["name"],
            seed=data["seed"],
            years=tuple(data["years"]),
            discount_rate=data["discount_rate"],
            capital_budget=data["capital_budget"],
            budget={int(y): v for y, v in data["budget"].items()},
            region_budget={pair(k): v for k, v in data["region_budget"].items()},
            region_floor=dict(data["region_floor"]),
            crews={pair(k): v for k, v in data["crews"].items()},
            assets=tuple(Asset(**a) for a in data["assets"]),
            projects=tuple(
                Project(**{**p, "cost_profile": tuple(p["cost_profile"]),
                           "npv": {int(y): v for y, v in p["npv"].items()}})
                for p in data["projects"]
            ),
        )

    def to_json(self) -> str:
        """Canonical JSON: sorted keys, no spaces, so equal portfolios give equal bytes."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def content_hash(self) -> str:
        """sha256 of the canonical JSON: a portfolio's identity in a run manifest."""
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()
