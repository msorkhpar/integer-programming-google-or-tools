import numpy_financial as npf
import pytest

from bus import lifecycle_cost


def flows(price, running, life, one_offs, resale):
    """The bus's costs year by year from today, as numpy-financial's npv wants them."""
    values = [price] + [running] * life
    for year, cost in one_offs.items():
        values[year] += cost
    values[life] -= resale
    return values


def test_with_no_discounting_every_cost_counts_in_full():
    assert lifecycle_cost(900, 60, 12, 0.0, {6: 150}, 50) == pytest.approx(900 + 60 * 12 + 150 - 50)


def test_running_costs_are_paid_at_the_end_of_each_year():
    assert lifecycle_cost(900, 60, 12, 0.05, {}, 0) == pytest.approx(npf.npv(0.05, flows(900, 60, 12, {}, 0)))


def test_a_one_off_cost_is_discounted_from_its_year():
    expected = npf.npv(0.05, flows(900, 60, 12, {6: 150}, 0))
    assert lifecycle_cost(900, 60, 12, 0.05, {6: 150}, 0) == pytest.approx(expected)


def test_the_resale_value_is_discounted_from_the_end_of_life():
    expected = npf.npv(0.05, flows(900, 60, 12, {6: 150}, 50))
    assert lifecycle_cost(900, 60, 12, 0.05, {6: 150}, 50) == pytest.approx(expected)
