import pytest

from floor_prices import next_prices

FLOORS = {2027: 100.0, 2028: 100.0, 2029: 100.0}


def test_prices_stay_put_when_the_bound_meets_the_best_plan():
    prices = {2027: 0.4, 2028: 0.7, 2029: 0.1}
    out = next_prices(prices, FLOORS, {2027: 90, 2028: 120, 2029: 100}, 5000, 5000, 2.0)
    assert out == pytest.approx(prices)


def test_a_year_short_of_its_floor_gets_a_higher_price():
    prices = {2027: 1.0, 2028: 1.0, 2029: 1.0}
    out = next_prices(prices, FLOORS, {2027: 90, 2028: 110, 2029: 100}, 1200, 1000, 1.0)
    assert out[2027] > 1.0 and out[2028] < 1.0 and out[2029] == pytest.approx(1.0)


def test_a_price_never_goes_below_zero():
    prices = {2027: 0.2, 2028: 0.2, 2029: 0.2}
    out = next_prices(prices, FLOORS, {2027: 100, 2028: 300, 2029: 100}, 2000, 1000, 2.0)
    assert out[2028] == 0.0
    assert all(v >= 0 for v in out.values())


def test_the_step_divides_by_the_squared_length():
    prices = {2027: 1.0, 2028: 1.0, 2029: 1.0}
    # g = (veg - F) = (-30, 40, 0), |g|^2 = 2500, step = 1.0 * (1250 - 1000) / 2500 = 0.1
    out = next_prices(prices, FLOORS, {2027: 70, 2028: 140, 2029: 100}, 1250, 1000, 1.0)
    assert out == pytest.approx({2027: 4.0, 2028: 0.0, 2029: 1.0})
    out = next_prices(prices, FLOORS, {2027: 70, 2028: 140, 2029: 100}, 1050, 1000, 1.0)
    assert out == pytest.approx({2027: 1.6, 2028: 0.2, 2029: 1.0})


def test_a_plan_on_every_floor_keeps_the_prices():
    prices = {2027: 0.3, 2028: 0.0, 2029: 0.9}
    out = next_prices(prices, FLOORS, {2027: 100, 2028: 100, 2029: 100}, 3000, 1000, 2.0)
    assert out == pytest.approx(prices)
