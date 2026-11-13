"""Write a GridCap portfolio as CSV files, and read it back.

Five flat files, the shape a planning database export has:

| file | one row per |
| --- | --- |
| `projects.csv` | project; `cost_profile` is the yearly spend joined by `;` |
| `npv.csv` | project and start year |
| `assets.csv` | asset |
| `budgets.csv` | year and region; region `ALL` is the year's total budget, year `0` a region's floor |
| `crews.csv` | program and year |

`portfolio.json` beside them holds the scalars (name, seed, years, rate, capital budget).
"""

from __future__ import annotations

import csv
import json
from dataclasses import fields
from pathlib import Path

from .portfolio import Asset, Portfolio, Project

PROJECT_COLUMNS = ("project_id", "name", "program", "region", "asset_id", "intervention", "cost_profile",
                   "earliest_start", "latest_start", "must_do", "parent", "parent_lag", "alt_group",
                   "crew_months")


def save_csv(portfolio: Portfolio, folder: str | Path) -> Path:
    """Write the portfolio's CSV files into `folder` (created if missing) and return it."""
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "projects.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(PROJECT_COLUMNS)
        for p in portfolio.projects:
            writer.writerow([p.project_id, p.name, p.program, p.region, p.asset_id, p.intervention,
                             ";".join(str(c) for c in p.cost_profile), p.earliest_start, p.latest_start,
                             int(p.must_do), p.parent or "", p.parent_lag, p.alt_group or "", p.crew_months])
    with (out / "npv.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("project_id", "start_year", "npv"))
        for p in portfolio.projects:
            for year, value in p.npv.items():
                writer.writerow((p.project_id, year, value))
    with (out / "assets.csv").open("w", newline="", encoding="utf-8") as handle:
        names = [f.name for f in fields(Asset)]
        writer = csv.writer(handle)
        writer.writerow(names)
        for a in portfolio.assets:
            writer.writerow([getattr(a, n) for n in names])
    with (out / "budgets.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("year", "region", "budget"))
        for year, value in portfolio.budget.items():
            writer.writerow((year, "ALL", value))
        for (region, year), value in portfolio.region_budget.items():
            writer.writerow((year, region, value))
        for region, value in portfolio.region_floor.items():
            writer.writerow((0, region, value))
    with (out / "crews.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("program", "year", "crew_months"))
        for (program, year), value in portfolio.crews.items():
            writer.writerow((program, year, value))
    scalars = {"name": portfolio.name, "seed": portfolio.seed, "years": list(portfolio.years),
               "discount_rate": portfolio.discount_rate, "capital_budget": portfolio.capital_budget}
    (out / "portfolio.json").write_text(json.dumps(scalars, indent=2) + "\n", encoding="utf-8")
    return out


def load_csv(folder: str | Path) -> Portfolio:
    """Read the files `save_csv` wrote. It trusts them: validation is the caller's job."""
    src = Path(folder)
    scalars = json.loads((src / "portfolio.json").read_text(encoding="utf-8"))
    npv: dict[str, dict[int, int]] = {}
    with (src / "npv.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            npv.setdefault(row["project_id"], {})[int(row["start_year"])] = int(row["npv"])
    projects = []
    with (src / "projects.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            projects.append(Project(
                project_id=row["project_id"], name=row["name"], program=row["program"], region=row["region"],
                asset_id=row["asset_id"], intervention=row["intervention"],
                cost_profile=tuple(int(c) for c in row["cost_profile"].split(";")),
                earliest_start=int(row["earliest_start"]), latest_start=int(row["latest_start"]),
                must_do=row["must_do"] == "1", parent=row["parent"] or None, parent_lag=int(row["parent_lag"]),
                alt_group=row["alt_group"] or None, crew_months=int(row["crew_months"]),
                npv=npv.get(row["project_id"], {})))
    assets = []
    with (src / "assets.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            assets.append(Asset(asset_id=row["asset_id"], kind=row["kind"], region=row["region"],
                                age=int(row["age"]), weibull_beta=float(row["weibull_beta"]),
                                weibull_eta=float(row["weibull_eta"]), rul=int(row["rul"]), cof=int(row["cof"])))
    budget, region_budget, floor = {}, {}, {}
    with (src / "budgets.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            year, region, value = int(row["year"]), row["region"], int(row["budget"])
            if region == "ALL":
                budget[year] = value
            elif year == 0:
                floor[region] = value
            else:
                region_budget[(region, year)] = value
    crews = {}
    with (src / "crews.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            crews[(row["program"], int(row["year"]))] = int(row["crew_months"])
    return Portfolio(name=scalars["name"], seed=scalars["seed"], years=tuple(scalars["years"]),
                     discount_rate=scalars["discount_rate"], projects=tuple(projects), assets=tuple(assets),
                     capital_budget=scalars["capital_budget"], budget=budget, region_budget=region_budget,
                     region_floor=floor, crews=crews)
