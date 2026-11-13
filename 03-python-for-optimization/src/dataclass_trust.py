"""A dataclass built from a CSV row keeps the strings it was given, whatever its annotations say."""

import csv
from dataclasses import FrozenInstanceError, dataclass

from export import tiny_export


@dataclass(frozen=True)
class ProjectRecord:
    project_id: str
    cost_profile: tuple[int, ...]
    must_do: bool


with tiny_export() as folder:
    with (folder / "projects.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["project_id"]: row for row in csv.DictReader(handle)}


def record(row: dict[str, str]) -> ProjectRecord:
    return ProjectRecord(row["project_id"], row["cost_profile"], row["must_do"])


p001, p003 = record(rows["P001"]), record(rows["P003"])
print(p003)
print("type of cost_profile:", type(p003.cost_profile).__name__)
print("P003 lasts", len(p003.cost_profile), "years")
print("P001 is must-do:", bool(p001.must_do))
try:
    print(sum(p003.cost_profile))
except TypeError as error:
    print("sum(cost_profile) fails:", error)

try:
    p003.must_do = True
except FrozenInstanceError as error:
    print("assigning a field fails:", error)
