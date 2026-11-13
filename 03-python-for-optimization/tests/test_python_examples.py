"""The module 03 examples compute what their lessons say they print."""

import csv

import pandas as pd
import pytest

from export import BAD_ROWS, TYPES, dirty_export, tiny_export


def rows_of(folder) -> list[dict[str, str]]:
    with (folder / "projects.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_typed_read_gives_the_model_its_sets_and_parameters():
    from to_parameters import parameters
    with tiny_export() as folder:
        data = parameters(pd.read_csv(folder / "projects.csv", dtype=TYPES), pd.read_csv(folder / "npv.csv"), 7390)
    assert data["M"] == {"P002"} and data["parent"] == {"P004": "P003"} and data["G"] == {"G006": ["P006", "P007"]}
    assert sum(data["capex"].values()) == 13_440 and data["npv"]["P004"] == 2120


def test_every_bad_row_is_masked_with_its_reason():
    from reject_rows import rejections
    with dirty_export() as folder:
        report = rejections(pd.read_csv(folder / "projects.csv", dtype=TYPES))
    assert list(report["line"]) == [9, 10, 11, 12, 13, 14, 15]
    assert set(report["reason"]) == {"cost is not a number", "negative cost", "earliest start after latest",
                                     "unknown region", "duplicate id", "unknown parent"}
    assert len(BAD_ROWS) == 6


def test_pydantic_converts_a_good_row():
    from pydantic_rows import ProjectRow
    with tiny_export() as folder:
        rows = rows_of(folder)
    p003 = ProjectRow.model_validate(rows[2])
    assert p003.cost_profile == (980, 1490) and p003.parent is None and p003.must_do is False
    assert ProjectRow.model_validate(rows[3]).parent == "P003"


def test_the_pydantic_loader_rejects_the_same_lines_as_the_pandas_check():
    from load_portfolio import load
    from reject_rows import rejections
    with dirty_export() as folder:
        projects, rejected = load(rows_of(folder))
        frame = pd.read_csv(folder / "projects.csv", dtype=TYPES)
    assert [p.project_id for p in projects] == ["P001", "P002", "P003", "P004", "P005", "P006", "P007"]
    assert {r[0] for r in rejected} == set(rejections(frame)["line"])


def test_two_formulas_for_one_present_value_differ_only_within_tolerance(capsys):
    from float_compare import a, b
    assert a != b and a == pytest.approx(b, rel=1e-15)


def test_every_parametrized_case_names_a_rejection():
    from bad_row_cases import CASES
    from load_portfolio import load
    with dirty_export() as folder:
        _, rejected = load(rows_of(folder))
    for project_id, reason in CASES:
        assert any(pid == project_id and reason in why for _, pid, why in rejected)


def test_the_exact_present_value_test_fails_and_the_tolerant_one_passes():
    from first_tests import RATE, present_value
    assert present_value(2150, 1) != 2150 * (1 + RATE) ** -1
    assert present_value(2150, 1) == pytest.approx(2150 * (1 + RATE) ** -1)
