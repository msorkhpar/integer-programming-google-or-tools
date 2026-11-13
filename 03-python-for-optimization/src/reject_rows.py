"""Check every row of a dirty projects.csv with one boolean mask per rule, and reject the bad rows."""

import pandas as pd

from export import TYPES, dirty_export
from gridcap import REGIONS


def rejections(projects: pd.DataFrame) -> pd.DataFrame:
    """One row per (bad row, broken rule): the file's line number, the project id and the reason."""
    amounts = pd.to_numeric(projects["cost_profile"].str.split(";").explode(), errors="coerce")
    rules = {
        "cost is not a number": amounts.isna().groupby(level=0).any(),
        "negative cost": (amounts < 0).groupby(level=0).any(),
        "earliest start after latest": projects["earliest_start"] > projects["latest_start"],
        "unknown region": ~projects["region"].isin(REGIONS),
        "duplicate id": projects["project_id"].duplicated(keep=False),
        "unknown parent": projects["parent"].notna() & ~projects["parent"].isin(projects["project_id"]),
    }
    found = [projects.loc[mask, ["project_id"]].assign(reason=reason) for reason, mask in rules.items()]
    report = pd.concat(found).sort_index()
    return report.assign(line=report.index + 2)[["line", "project_id", "reason"]]


if __name__ == "__main__":
    with dirty_export() as folder:
        projects = pd.read_csv(folder / "projects.csv", dtype=TYPES)
        npv = pd.read_csv(folder / "npv.csv")
    print("the six rows appended to the export:")
    print(projects.tail(6)[["project_id", "region", "cost_profile", "earliest_start", "latest_start",
                             "parent"]].to_string(index=False))

    report = rejections(projects)
    clean = projects.drop(index=report.index.unique())
    print()
    print(report.to_string(index=False))
    print()
    print(f"{len(projects)} rows read, {report.index.nunique()} rejected, {len(clean)} kept:",
          " ".join(clean["project_id"]))

    # npv.csv's key is a pair of columns. Type P001's 2028 value in a second time, differently.
    twice = pd.concat([npv, npv.head(1).assign(npv=1500)], ignore_index=True)
    same_key = twice.duplicated(subset=["project_id", "start_year"], keep=False)
    print()
    print("labels of the rows sharing a (project_id, start_year):", twice.index[same_key].tolist())
    print(twice[same_key].to_string())
    print("to_dict keeps one of them:", twice.set_index(["project_id", "start_year"])["npv"].to_dict()["P001", 2028])
