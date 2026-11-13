import numpy_financial as npf
import pytest

from start_table import npv_by_start_year


def test_without_discounting_or_escalation_each_start_nets_the_same():
    table = npv_by_start_year((400, 400), 90, 20, (2027, 2028, 2029), 2027, 0.0, 0.0)
    assert table == pytest.approx({2027: 1000, 2028: 1000, 2029: 1000})


def test_benefits_begin_the_year_after_the_work_ends():
    table = npv_by_start_year((400, 400), 90, 3, (2027,), 2027, 0.06, 0.0)
    assert table[2027] == pytest.approx(npf.npv(0.06, [-400, -400, 90, 90, 90]))


def test_every_start_is_valued_on_the_valuation_date():
    table = npv_by_start_year((400, 400), 90, 3, (2027, 2029), 2027, 0.06, 0.0)
    assert table[2027] == pytest.approx(npf.npv(0.06, [-400, -400, 90, 90, 90]))
    assert table[2029] == pytest.approx(npf.npv(0.06, [0, 0, -400, -400, 90, 90, 90]))


def test_prices_escalate_from_the_valuation_year():
    real = [0, -400, -400, 90, 90, 90]                      # start 2028, in 2027 prices
    nominal = [a * 1.03 ** i for i, a in enumerate(real)]   # i years after 2027
    table = npv_by_start_year((400, 400), 90, 3, (2028,), 2027, 0.06, 0.03)
    assert table[2028] == pytest.approx(npf.npv(0.06, nominal))
