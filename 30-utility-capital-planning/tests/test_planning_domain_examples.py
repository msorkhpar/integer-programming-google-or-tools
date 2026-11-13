"""The module 30 examples: the portfolio by program, a revenue requirement, the fleets, a planning cycle."""

import pytest

from gridcap import PROGRAMS, REGIONS, generate
from cycle_model import Scenario, base_scenario, build, optimize, spend_of


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.fixture(scope="module")
def base_run(small):
    return optimize(base_scenario(small))


def test_the_portfolio_asks_for_more_than_the_budgets(small):
    asked = sum(p.capex for p in small.projects)
    assert asked == 69_810
    assert sum(small.budget.values()) == 42_230
    assert {prog: sum(p.capex for p in small.projects if p.program == prog) for prog in PROGRAMS} == {
        "transmission": 43_990, "distribution": 21_920, "vegetation": 3_900}


def test_the_revenue_requirement_returns_the_capital_and_a_return():
    from revenue_requirement import schedule
    rows = schedule(5_310, 30, 0.075)
    assert sum(r[2] for r in rows) == pytest.approx(5_310)
    assert rows[0][4] == pytest.approx(177 + 0.075 * (5_310 - 88.5))
    assert sum(r[4] for r in rows) == pytest.approx(11_284, abs=1)


def test_the_base_plan_keeps_every_rule(small, base_run):
    assert base_run.status == "OPTIMAL"
    assert base_run.npv == pytest.approx(24_260)
    assert len(base_run.starts) == 27
    spend = spend_of(small, base_run.starts)
    assert all(spend[y] <= small.budget[y] for y in small.years)
    assert all(base_run.starts.get(p.project_id) for p in small.projects if p.must_do)
    for r in REGIONS:
        got = sum(small.project(i).capex for i in base_run.starts if small.project(i).region == r)
        assert got >= small.region_floor[r]


def test_a_snapshot_changes_with_the_inputs_only(small):
    a, b = base_scenario(small), base_scenario(small, name="copy")
    assert a.snapshot() == b.snapshot()
    b.budget[2029] = 6_000
    assert a.snapshot() != b.snapshot()
    c = base_scenario(small)
    c.force_in = {"P024"}
    assert c.snapshot() != a.snapshot()


def test_the_cut_and_the_override_cost_what_the_lesson_says(small, base_run):
    cut = Scenario("cut", small, {**small.budget, 2029: 6_000}, dict(small.region_floor))
    assert optimize(cut).npv == pytest.approx(23_086)
    forced = base_scenario(small)
    forced.force_in = {"P024"}
    run = optimize(forced)
    assert base_run.npv - run.npv == pytest.approx(273)
    assert "P024" in run.starts


def test_force_out_removes_a_project(small):
    s = base_scenario(small)
    s.force_out = {"P032"}
    run = optimize(s)
    assert "P032" not in run.starts
    assert "out_P032" in {c.name for c in build(s).model.linear_constraints()}
