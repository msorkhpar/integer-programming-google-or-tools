"""The files a planning database exports for GridCap, written to a temporary folder.

GridCap is a fictional utility. `tiny_export()` writes the tiny portfolio's CSV files with
`gridcap.save_csv`; `dirty_export()` writes the same files with six bad project rows appended,
the kind of rows a hand-edited spreadsheet sends back.
"""

from __future__ import annotations

import csv
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from gridcap import generate, save_csv

#: The type of every column whose guessed type depends on what the file holds.
TYPES = {"project_id": str, "region": str, "cost_profile": str, "parent": str, "alt_group": str,
         "earliest_start": "int64", "latest_start": "int64", "must_do": bool}

#: Six bad rows, each breaking one rule. Every other column is copied from P008.
BAD_ROWS = [
    {"project_id": "P009", "cost_profile": "1,250"},                              # not a number
    {"project_id": "P010", "cost_profile": "-400"},                               # negative cost
    {"project_id": "P011", "earliest_start": "2029", "latest_start": "2027"},     # window reversed
    {"project_id": "P012", "region": "Hills"},                                    # unknown region
    {"project_id": "P008"},                                                       # duplicate id
    {"project_id": "P013", "parent": "P099", "parent_lag": "1"},                  # unknown parent
]


@contextmanager
def tiny_export() -> Iterator[Path]:
    """A folder holding the tiny portfolio's CSV files, deleted when the block ends."""
    with tempfile.TemporaryDirectory(prefix="gridcap-") as folder:
        yield save_csv(generate("tiny"), folder)


@contextmanager
def dirty_export() -> Iterator[Path]:
    """The tiny export with `BAD_ROWS` appended to projects.csv."""
    with tiny_export() as folder:
        path = folder / "projects.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        template = next(r for r in rows if r["project_id"] == "P008")
        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(template))
            for change in BAD_ROWS:
                writer.writerow({**template, **change})
        yield folder
