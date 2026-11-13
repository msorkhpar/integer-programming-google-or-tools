"""One parametrized test, one case per bad row of the dirty export; run this file to run them."""

import csv
import os
from pathlib import Path

import pytest

from export import dirty_export
from load_portfolio import load

CASES = [
    ("P009", "unable to parse string as an integer"),
    ("P010", "greater than or equal to 0"),
    ("P011", "earliest start after latest"),
    ("P012", "Input should be 'Ridge'"),
    ("P008", "duplicate id"),
    ("P013", "unknown parent"),
]


@pytest.fixture(scope="module")
def rejected() -> list[tuple[int, str, str]]:
    with dirty_export() as folder:
        with (folder / "projects.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    return load(rows)[1]


@pytest.mark.parametrize(("project_id", "reason"), CASES, ids=[pid for pid, _ in CASES])
def test_bad_row_is_rejected_for_its_rule(rejected, project_id, reason):
    assert any(pid == project_id and reason in why for _, pid, why in rejected)


def test_good_rows_are_not_rejected(rejected):
    assert not {pid for _, pid, _ in rejected} & {"P001", "P002", "P003", "P004", "P005", "P006", "P007"}


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    raise SystemExit(pytest.main(["-v", "--no-header", "-p", "no:cacheprovider", "--rootdir", ".", Path(__file__).name]))
