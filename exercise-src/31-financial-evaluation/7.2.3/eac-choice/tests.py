import numpy_financial as npf
import pytest

from choose import cheapest, present_cost, yearly_cost


def test_options_with_equal_lives_rank_by_cost():
    options = {"overhaul": (500, 30, 10), "patch": (400, 45, 10)}
    assert cheapest(options, 0.05) == "overhaul"
    assert cheapest(options, 0.0) == "overhaul"
    assert yearly_cost(500, 30, 10, 0.0) == pytest.approx(80.0)


def test_a_longer_life_can_win_despite_a_higher_present_cost():
    options = {"patch": (200, 130, 8), "rebuild": (1500, 20, 35)}
    assert present_cost(1500, 20, 35, 0.06) > present_cost(200, 130, 8, 0.06)
    assert cheapest(options, 0.06) == "rebuild"


def test_the_yearly_cost_charges_for_money_tied_up():
    assert yearly_cost(1000, 0, 40, 0.08) == pytest.approx(-npf.pmt(0.08, 40, 1000))
    assert cheapest({"rebuild": (1000, 0, 40), "patch": (0, 60, 10)}, 0.08) == "patch"
