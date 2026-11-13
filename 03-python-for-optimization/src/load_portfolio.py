"""Load projects.csv into typed rows: check each row alone, then the rules that span rows."""

import csv
from collections import Counter

import pandas as pd
from pydantic import ValidationError

from export import TYPES, dirty_export
from pydantic_rows import ProjectRow, reasons
from reject_rows import rejections


def load(rows: list[dict[str, str]]) -> tuple[list[ProjectRow], list[tuple[int, str, str]]]:
    """The rows that pass every rule, and (file line, project id, reason) for each that does not."""
    parsed, rejected = [], []
    for line, row in enumerate(rows, start=2):
        try:
            parsed.append((line, ProjectRow.model_validate(row)))
        except ValidationError as error:
            rejected += [(line, row["project_id"], reason) for reason in reasons(error)]

    copies = Counter(p.project_id for _, p in parsed)
    rejected += [(line, p.project_id, "duplicate id") for line, p in parsed if copies[p.project_id] > 1]
    kept = [(line, p) for line, p in parsed if copies[p.project_id] == 1]
    known = {p.project_id for _, p in kept}
    rejected += [(line, p.project_id, "unknown parent") for line, p in kept if p.parent and p.parent not in known]
    kept = [(line, p) for line, p in kept if not p.parent or p.parent in known]
    return [p for _, p in kept], sorted(rejected)


if __name__ == "__main__":
    with dirty_export() as folder:
        with (folder / "projects.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        frame = pd.read_csv(folder / "projects.csv", dtype=TYPES)

    projects, rejected = load(rows)
    for line, project_id, reason in rejected:
        print(f"line {line:2}  {project_id}  {reason}")
    print()
    print(f"{len(rows)} rows read, {len({r[0] for r in rejected})} rejected, {len(projects)} kept:",
          " ".join(p.project_id for p in projects))
    print("same lines as the pandas check of lesson 1.3.1:",
          {r[0] for r in rejected} == set(rejections(frame)["line"]))
