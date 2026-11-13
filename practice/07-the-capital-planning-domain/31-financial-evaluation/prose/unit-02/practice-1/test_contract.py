import pytest

from contract import billed


def test_each_year_of_work_lands_in_its_calendar_year():
    assert billed((400, 250, 120), 2026, 2029, 0.0) == pytest.approx({2029: 400, 2030: 250, 2031: 120})


def test_a_later_start_pays_later_prices():
    bills = billed((400, 250), 2026, 2029, 0.04)
    assert bills == pytest.approx({2029: 400 * 1.04 ** 3, 2030: 250 * 1.04 ** 4})


def test_work_in_the_price_book_year_is_billed_as_quoted():
    bills = billed((400, 250), 2026, 2026, 0.04)
    assert bills == pytest.approx({2026: 400, 2027: 250 * 1.04})
