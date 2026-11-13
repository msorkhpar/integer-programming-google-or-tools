"""Turn GridCap's exported tables into the sets and dicts the selection model of lesson 1.1.1 indexes."""

import json

import pandas as pd

from export import TYPES, tiny_export
from gridcap import generate


def parameters(projects: pd.DataFrame, npv: pd.DataFrame, budget: int) -> dict:
    """The model's sets and parameters, as plain Python sets and dicts keyed by project id."""
    capex = {pid: sum(int(c) for c in profile.split(";"))
             for pid, profile in zip(projects["project_id"], projects["cost_profile"])}
    npv_at = npv.set_index(["project_id", "start_year"])["npv"].to_dict()
    value = {pid: npv_at[pid, start] for pid, start in zip(projects["project_id"], projects["earliest_start"])}
    children = projects[projects["parent"].notna()]
    grouped = projects[projects["alt_group"].notna()]
    return {
        "P": list(projects["project_id"]),
        "M": set(projects.loc[projects["must_do"], "project_id"]),
        "parent": dict(zip(children["project_id"], children["parent"])),
        "G": {g: sorted(ids) for g, ids in grouped.groupby("alt_group")["project_id"]},
        "capex": capex,
        "npv": value,
        "B": budget,
    }


if __name__ == "__main__":
    with tiny_export() as folder:
        projects = pd.read_csv(folder / "projects.csv", dtype=TYPES)
        npv = pd.read_csv(folder / "npv.csv")
        budget = json.loads((folder / "portfolio.json").read_text(encoding="utf-8"))["capital_budget"]
        print("the export:", sorted(path.name for path in folder.iterdir()))
        print()

    print("npv.csv is long: one row per project and start year")
    print(npv.head(4).to_string(index=False))
    print()
    print("pivoted for a reader (start years as columns):")
    print(npv.pivot(index="project_id", columns="start_year", values="npv").head(4))

    data = parameters(projects, npv, budget)
    print()
    for name in ("M", "parent", "G", "capex", "npv", "B"):
        print(f"{name:7}", data[name])

    tiny = generate("tiny")
    same = (data["capex"] == {p.project_id: p.capex for p in tiny.projects}
            and data["npv"] == {p.project_id: p.value for p in tiny.projects})
    print()
    print("capex and npv match generate('tiny'):", same)
