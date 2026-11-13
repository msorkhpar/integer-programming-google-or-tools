import pytest

from certify import certify

# A print shop's week: runs of brochures, catalogues and calendars, profit per run.
VALUE = {"brochure": 4, "catalogue": 4, "calendar": 3}
ROWS = {
    "labour": ({"brochure": 2, "catalogue": 1, "calendar": 1}, "<=", 10),
    "press": ({"brochure": 1, "catalogue": 2, "calendar": 1}, "<=", 12),
    "foil": ({"brochure": 1}, "<=", 4),
}


def test_the_best_plan_is_certified_and_a_worse_one_refused():
    prices = certify(VALUE, ROWS, {"brochure": 0, "catalogue": 2, "calendar": 8})
    assert prices == pytest.approx({"labour": 2, "press": 1, "foil": 0})
    assert certify(VALUE, ROWS, {"brochure": 4, "catalogue": 0, "calendar": 2}) is None


def test_a_binding_minimum_takes_a_negative_price():
    rows = {**ROWS, "min_brochure": ({"brochure": 1}, ">=", 1)}
    prices = certify(VALUE, rows, {"brochure": 1, "catalogue": 3, "calendar": 5})
    assert prices == pytest.approx({"labour": 2, "press": 1, "foil": 0, "min_brochure": -1})


def test_a_product_left_out_that_would_pay_refuses_the_plan():
    assert certify(VALUE, ROWS, {"brochure": 0, "catalogue": 0, "calendar": 10}) is None
    assert certify(VALUE, ROWS, {"brochure": 0, "catalogue": 2, "calendar": 8}) is not None
