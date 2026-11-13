import pytest

from bound import price_bound

# A transit agency's maintenance LP: $k spent on buses, rail and ferries, value per $k spent.
VALUE = {"bus": 0.5, "rail": 0.8, "ferry": 0.3}
ROWS = {
    "budget": ({"bus": 1, "rail": 1, "ferry": 1}, 800),
    "depot": ({"bus": 1}, 400),
    "track": ({"rail": 1}, 300),
    "dock": ({"ferry": 1}, 200),
}
ZERO = {name: 0.0 for name in ROWS}


def test_covering_prices_prove_their_bound_and_others_prove_nothing():
    assert price_bound(VALUE, ROWS, {**ZERO, "budget": 0.9}) == pytest.approx(720)
    assert price_bound(VALUE, ROWS, {**ZERO, "budget": 0.35, "track": 0.5, "depot": 0.2}) == pytest.approx(510)
    assert price_bound(VALUE, ROWS, {**ZERO, "budget": 0.3}) is None


def test_prices_that_cover_exactly_are_enough():
    assert price_bound(VALUE, ROWS, {**ZERO, "budget": 0.3, "track": 0.5, "depot": 0.2}) == pytest.approx(470)


def test_a_negative_price_proves_nothing():
    assert price_bound(VALUE, ROWS, {**ZERO, "budget": 0.9, "dock": -0.5}) is None
    assert price_bound(VALUE, ROWS, {**ZERO, "budget": 0.9, "dock": 0.5}) == pytest.approx(820)


def test_an_activity_in_no_row_cannot_be_covered():
    signals = {**VALUE, "signals": 0.1}
    assert price_bound(signals, ROWS, {**ZERO, "budget": 0.9}) is None
    assert price_bound({**VALUE, "signals": 0.0}, ROWS, {**ZERO, "budget": 0.9}) == pytest.approx(720)


def test_a_price_counts_once_per_unit_of_coefficient():
    staffed = {**ROWS, "staff": ({"bus": 2, "rail": 3, "ferry": 1}, 2000)}
    prices = {**ZERO, "staff": 0.4}
    assert price_bound(VALUE, staffed, prices) == pytest.approx(800)
    assert price_bound(VALUE, staffed, {**prices, "staff": 0.2}) is None
