import math

import pytest

from trim_builder import TrimResult, build_result

WORK = {"C-2": (4, 60), "C-5": (3, 100), "C-7": (4, 90), "C-9": (5, 40)}
CAPACITY = {5: 80, 3: 160, 4: 160}          # given out of order on purpose


def test_an_optimal_result_has_hours_by_month_and_no_gap():
    r = build_result("optimal", "Best plan found and proven.", 240.0, 240.0, ["C-7", "C-5", "C-2"], WORK,
                     {3: 160, 4: 160})
    assert r.circuits == ["C-2", "C-5", "C-7"] and r.gap == 0.0 and r.bound == 240.0
    assert [(m.month, m.crew_hours, m.capacity) for m in r.hours_by_month] == [(3, 100, 160), (4, 150, 160)]


def test_a_month_with_no_work_still_has_its_row():
    r = build_result("optimal", "ok", 50.0, 50.0, ["C-9"], WORK, {3: 160, 4: 160, 5: 80})
    assert [(m.month, m.crew_hours) for m in r.hours_by_month] == [(3, 0), (4, 0), (5, 40)]


def test_months_come_in_order():
    r = build_result("optimal", "ok", 50.0, 50.0, ["C-9", "C-5"], WORK, {5: 80, 3: 160})
    assert [m.month for m in r.hours_by_month] == [3, 5]


def test_the_gap_is_measured_against_the_plan_value():
    r = build_result("time_limit", "Stopped at the limit.", 200.0, 250.0, ["C-5"], WORK, CAPACITY)
    assert r.gap == pytest.approx(0.25)


def test_an_infinite_bound_becomes_null_and_reads_back():
    r = build_result("time_limit", "No plan found within the limit.", None, math.inf, [], WORK, CAPACITY)
    assert r.bound is None and r.gap is None and r.hours_by_month == []
    assert TrimResult.model_validate_json(r.model_dump_json()) == r
    finite = build_result("time_limit", "No plan found within the limit.", None, 500.0, [], WORK, CAPACITY)
    assert finite.bound == 500.0 and finite.gap is None


def test_a_plan_worth_zero_has_a_gap():
    r = build_result("time_limit", "Stopped at the limit.", 0.0, 3.0, [], WORK, CAPACITY)
    assert r.gap == pytest.approx(3.0)


def test_a_bound_just_below_the_value_gives_a_gap_of_zero():
    r = build_result("optimal", "Best plan found and proven.", 240.0, 239.9999, ["C-5"], WORK, CAPACITY)
    assert r.gap == 0.0
