"""GridCap as the tables a planning export has, read into pandas DataFrames.

`gridcap.save_csv` writes the portfolio as flat CSV files; `read_tables` reads the ones the timing
model needs. GridCap is fictional: the tables describe no real utility.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from gridcap import Portfolio, save_csv


@dataclass(frozen=True)
class Tables:
    name: str
    projects: pd.DataFrame      # one row per project
    starts: pd.DataFrame        # one row per (project, allowed start year), with its NPV
    costs: pd.DataFrame         # one row per (project, year of work k), with its amount
    budget: pd.DataFrame        # one row per year, the all-region budget


def read_tables(folder: str | Path, name: str) -> Tables:
    folder = Path(folder)
    projects = pd.read_csv(folder / "projects.csv", keep_default_na=False,
                           dtype={"parent": str, "alt_group": str, "cost_profile": str})
    starts = pd.read_csv(folder / "npv.csv").rename(columns={"start_year": "start"})
    # "360;720;1470" -> three rows, k = 0, 1, 2: the cost profile as a long table.
    costs = (projects[["project_id", "cost_profile"]]
             .assign(amount=projects["cost_profile"].str.split(";"))
             .explode("amount")
             .drop(columns="cost_profile"))
    costs["amount"] = costs["amount"].astype("int64")
    costs["k"] = costs.groupby("project_id").cumcount()
    costs = costs.reset_index(drop=True)[["project_id", "k", "amount"]]
    budgets = pd.read_csv(folder / "budgets.csv", keep_default_na=False)
    budget = (budgets[budgets["region"] == "ALL"][["year", "budget"]]
              .sort_values("year").reset_index(drop=True))
    projects = projects.drop(columns=["cost_profile"])
    projects["must_do"] = projects["must_do"].astype(bool)
    return Tables(name, projects, starts, costs, budget)


def tables_of(portfolio: Portfolio) -> Tables:
    """Write the portfolio's CSV files to a temporary folder and read them back as tables."""
    with tempfile.TemporaryDirectory() as folder:
        save_csv(portfolio, folder)
        return read_tables(folder, portfolio.name)


if __name__ == "__main__":
    from gridcap import generate

    t = tables_of(generate("small"))
    with pd.option_context("display.width", 120, "display.max_columns", 10):
        print(t.projects[["project_id", "region", "earliest_start", "latest_start", "must_do", "parent",
                          "parent_lag", "alt_group"]].head(4).to_string(index=False))
        print()
        print(t.starts.head(4).to_string(index=False))
        print()
        print(t.costs.head(4).to_string(index=False))
        print()
        print(t.budget.to_string(index=False))
    print(f"\n{len(t.projects)} projects, {len(t.starts)} start rows, {len(t.costs)} cost rows, "
          f"{len(t.budget)} years")
