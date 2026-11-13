import math

import pytest

from forecast import forecast

INF = math.inf


def test_a_raise_inside_the_range_moves_the_objective_by_the_price():
    assert forecast(5000.0, 0.8, 1200.0, 900.0, 1500.0, 1300.0) == pytest.approx(5080.0)
    assert forecast(20.0, 3.0, 4.0, 0.0, INF, 104.0) == pytest.approx(320.0)


def test_a_cut_inside_the_range_moves_it_back_by_the_price():
    assert forecast(5000.0, 0.8, 1200.0, 900.0, 1500.0, 1000.0) == pytest.approx(4840.0)


def test_outside_the_range_there_is_no_forecast():
    assert forecast(5000.0, 0.8, 1200.0, 900.0, 1500.0, 1600.0) is None
    assert forecast(5000.0, 0.8, 1200.0, 900.0, 1500.0, 850.0) is None
    assert forecast(5000.0, 0.8, 1200.0, 900.0, 1500.0, 1450.0) == pytest.approx(5200.0)


def test_the_ends_of_the_range_are_inside():
    assert forecast(5000.0, 0.8, 1200.0, 900.0, 1500.0, 1500.0) == pytest.approx(5240.0)
    assert forecast(5000.0, 0.8, 1200.0, 900.0, 1500.0, 900.0) == pytest.approx(4760.0)


def test_a_minimizations_negative_price_lowers_the_cost():
    assert forecast(7000.0, -2.5, 300.0, 250.0, 400.0, 340.0) == pytest.approx(6900.0)
