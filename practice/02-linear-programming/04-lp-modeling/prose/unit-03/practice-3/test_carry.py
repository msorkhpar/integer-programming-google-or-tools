import pytest

from carry import plan_spending

BUDGETS = {2030: 100, 2031: 100, 2032: 100}
WORK = {2030: 60, 2031: 130, 2032: 150}
VALUE = {2030: 1.0, 2031: 0.9, 2032: 0.8}


def test_unspent_money_rolls_forward_and_is_spent_later():
    status, value, spend, carry = plan_spending(BUDGETS, WORK, VALUE, 0.5)
    assert status == "OPTIMAL"
    assert value == pytest.approx(265)
    assert spend == {2030: pytest.approx(60), 2031: pytest.approx(130), 2032: pytest.approx(110)}
    assert set(carry) == {2030, 2031, 2032}


def test_the_carry_cap_is_a_share_of_the_year_the_money_leaves():
    status, value, spend, carry = plan_spending({2030: 100, 2031: 200}, {2030: 50, 2031: 300},
                                                {2030: 1.0, 2031: 0.9}, 0.2)
    assert status == "OPTIMAL"
    assert carry[2030] <= 20 + 1e-6
    assert value == pytest.approx(248)


def test_the_first_year_has_nothing_carried_in():
    status, value, spend, carry = plan_spending({2030: 100, 2031: 100}, {2030: 150, 2031: 20},
                                                {2030: 1.0, 2031: 0.9}, 0.5)
    assert status == "OPTIMAL"
    assert spend[2030] == pytest.approx(100)
    assert value == pytest.approx(118)


def test_money_neither_spent_nor_carried_may_lapse():
    status, value, spend, carry = plan_spending({2030: 100, 2031: 100}, {2030: 30, 2031: 100},
                                                {2030: 1.0, 2031: 0.9}, 0.5)
    assert status == "OPTIMAL"
    assert value == pytest.approx(120)
