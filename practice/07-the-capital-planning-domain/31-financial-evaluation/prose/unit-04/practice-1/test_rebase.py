import pytest

from rebase import to_plan_date


def test_each_entry_is_moved_to_the_plans_date():
    table = to_plan_date({2027: 500, 2028: 500, 2029: 470}, 0.06, 2027)
    assert table == pytest.approx({2027: 500, 2028: 500 / 1.06, 2029: 470 / 1.06 ** 2})


def test_the_plans_date_may_precede_every_start():
    table = to_plan_date({2029: 800, 2030: 760}, 0.05, 2027)
    assert table == pytest.approx({2029: 800 / 1.05 ** 2, 2030: 760 / 1.05 ** 3})


def test_a_start_before_the_plans_date_is_carried_forward():
    table = to_plan_date({2025: 300, 2026: 310, 2027: 320}, 0.04, 2026)
    assert table == pytest.approx({2025: 300 * 1.04, 2026: 310, 2027: 320 / 1.04})
