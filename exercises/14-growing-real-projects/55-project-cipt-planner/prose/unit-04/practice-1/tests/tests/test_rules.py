"""Lesson 14.2.3: must-dos, alternatives, bundles and parents with lags."""

import pytest

from cipt.data import load_request
from cipt.model import build
from cipt.solve import solve
from conftest import export, row

TWO = (2027, 2028)


def test_must_do_is_funded_even_at_low_value():
    raw = export([row("A", (100,), 1, must_do=True), row("B", (100,), 90)], capital_budget=100)
    assert solve(load_request(raw)).funded == ("A",)


def test_alternatives_fund_at_most_one():
    raw = export([row("A", (100,), 90, alt_group="G"), row("B", (100,), 80, alt_group="G")])
    assert solve(load_request(raw)).funded == ("A",)


def test_bundle_is_all_or_nothing():
    raw = export([row("A", (100,), 100, bundle="K"), row("B", (100,), 1, bundle="K"), row("C", (100,), 60)],
                 capital_budget=200)
    assert solve(load_request(raw)).funded == ("A", "B")


def test_child_starts_a_lag_after_its_parent():
    raw = export([row("P", (50,), 10), row("C", (50,), 100, latest=2028, parent="P", lag=1),
                  row("D", (50,), 60, earliest=2028)], years=TWO, budget={2027: 50, 2028: 50})
    assert solve(load_request(raw)).starts == {"P": 2027, "C": 2028}


def test_child_is_not_funded_without_its_parent():
    raw = export([row("P", (100,), 1), row("C", (50,), 100, parent="P")], capital_budget=100)
    assert "C" not in solve(load_request(raw)).funded


def test_must_dos_beyond_the_budget_are_infeasible():
    raw = export([row("A", (100,), 5, must_do=True), row("B", (100,), 5, must_do=True)], capital_budget=150)
    assert solve(load_request(raw)).status == "infeasible"


def test_every_rule_has_a_named_row():
    raw = export([row("A", must_do=True), row("B", alt_group="G"), row("E", alt_group="G"),
                  row("C", bundle="K"), row("D", bundle="K"), row("F", latest=2028, parent="A", lag=1)],
                 years=TWO)
    names = set(build(load_request(raw)).rows)
    assert {"must_A", "alt_G", "bundle_C_D", "after_F_2027", "after_F_2028", "budget_2028"} <= names


def test_refuses_an_unknown_parent():
    with pytest.raises(ValueError, match="unknown parent"):
        load_request(export([row("C", parent="Z")]))
