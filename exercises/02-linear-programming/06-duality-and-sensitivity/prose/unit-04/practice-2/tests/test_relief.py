import pytest

from relief import worth_buying

# A port authority's options, each priced from its LP's shadow prices (value in $k).
BUDGET = {"name": "budget", "price": 0.4, "change": 1, "cost": 0.1, "units": 100}
BERTH = {"name": "berth", "price": 0.2, "change": 1, "cost": 0.25, "units": 50}


def test_an_offer_is_worth_its_price_less_its_cost_and_losses_are_dropped():
    assert worth_buying([BUDGET, BERTH]) == [("budget", pytest.approx(30))]


def test_a_unit_bought_may_move_a_row_by_many_units():
    crane = {"name": "crane_month", "price": 0.2, "change": 440, "cost": 60, "units": 3}
    assert worth_buying([BUDGET, crane]) == [("crane_month", pytest.approx(84)), ("budget", pytest.approx(30))]


def test_relief_from_a_requirement_lowers_it_and_gains_from_a_negative_price():
    waiver = {"name": "dredging_waiver", "price": -0.12, "change": -100, "cost": 5, "units": 2}
    assert worth_buying([BUDGET, waiver]) == [("budget", pytest.approx(30)), ("dredging_waiver", pytest.approx(14))]


def test_offers_are_ranked_by_their_total_gain():
    pilot = {"name": "pilot_hours", "price": 3.0, "change": 1, "cost": 2.0, "units": 20}
    tug = {"name": "tug_days", "price": 15.0, "change": 1, "cost": 5.0, "units": 1}
    assert worth_buying([tug, pilot]) == [("pilot_hours", pytest.approx(20)), ("tug_days", pytest.approx(10))]
