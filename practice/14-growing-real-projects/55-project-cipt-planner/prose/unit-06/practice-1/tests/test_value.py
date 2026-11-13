"""Lesson 14.2.4: NPV by start year, and the risk an intervention removes."""

import math

import pytest

from cipt import value
from cipt.data import load_request
from cipt.report import render
from cipt.solve import solve
from conftest import export, row

TWO, THREE = (2027, 2028), (2027, 2028, 2029)
#: beta = 1 makes the Weibull curve memoryless: every year's PoF is 1 - exp(-1/eta).
FLAT = {"id": "A-flat", "age": 5, "weibull_beta": 1.0, "weibull_eta": 10.0, "cof": 1000}


def test_npv_depends_on_the_start_year():
    # A is worth 500 only in 2027, and 2027 has no money; started in 2028 it is worth 100.
    raw = export([row("A", (100,), {2027: 500, 2028: 100}, latest=2028), row("B", (100,), 300, earliest=2028)],
                 years=TWO, budget={2027: 0, 2028: 100})
    plan = solve(load_request(raw))
    assert (plan.funded, plan.objective) == (("B",), 300)


def test_failure_probability_rises_with_age():
    assert value.annual_pof(2.0, 30.0, 20) > value.annual_pof(2.0, 30.0, 10) > 0


def test_annual_pof_follows_the_weibull_curve():
    assert value.annual_pof(1.0, 10.0, 5) == pytest.approx(1 - math.exp(-0.1))


def test_risk_reduction_counts_the_years_after_the_work():
    request = load_request(export([row("A", (100,), 50, latest=2028, asset=FLAT)], years=THREE))
    a, yearly = request.project("A"), 1000 * (1 - math.exp(-0.1))
    assert value.risk_reduction(request, a, 2027) == pytest.approx(2 * yearly)
    assert value.risk_reduction(request, a, 2028) == pytest.approx(yearly)


def test_risk_objective_funds_the_riskier_asset():
    risky = {**FLAT, "id": "A-risky", "cof": 5000}
    raw = export([row("A", (100,), 300, asset={**FLAT, "cof": 100}), row("B", (100,), 100, asset=risky)],
                 years=TWO, budget={2027: 100, 2028: 0}, objective="risk")
    assert solve(load_request(raw)).funded == ("B",)


def test_report_shows_npv_and_risk():
    raw = export([row("A", (100,), 300, asset=FLAT)], years=TWO, budget={2027: 100, 2028: 0})
    request = load_request(raw)
    assert "NPV $300k, risk reduced $95.2k (maximized: npv)" in render(request, solve(request))
