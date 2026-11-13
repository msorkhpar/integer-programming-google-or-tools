import pytest

from cipt.data import load_request
from cipt.plan import Plan
from cipt.report import render
from conftest import export, row


def test_reads_the_columns_it_uses():
    request = load_request(export([row("A", cost_profile=(100, 200), npv=50)]))
    a = request.project("A")
    assert (a.capex, a.value, a.earliest_start) == (300, 50, 2027)


def test_ignores_columns_it_does_not_use():
    raw = export([{**row("A"), "crew_months": 4}])
    assert load_request(raw).project("A").project_id == "A"


def test_refuses_duplicate_ids():
    with pytest.raises(ValueError, match="duplicate"):
        load_request(export([row("A"), row("A")]))


def test_report_lists_a_given_plan():
    request = load_request(export([row("A"), row("B")], capital_budget=500))
    text = render(request, Plan(status="optimal", starts={"B": 2027}, objective=100))
    assert "funded 1 of 2 projects" in text
    assert "B  start 2027" in text
