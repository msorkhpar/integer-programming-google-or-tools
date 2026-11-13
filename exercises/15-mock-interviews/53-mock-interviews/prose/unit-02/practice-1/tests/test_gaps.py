import math

import pytest

from gaps import gap_report


def test_a_maximization_divides_by_the_incumbent():
    report = gap_report(980.0, 1000.0)              # plan worth 980, nothing better than 1000
    assert report["absolute"] == pytest.approx(20.0)
    assert report["relative_highs"] == pytest.approx(20.0 / 980.0)
    assert report["relative_scip"] == pytest.approx(20.0 / 980.0)


def test_the_absolute_gap_has_no_sign():
    report = gap_report(1000.0, 980.0)              # a minimization: plan costs 1000, nothing below 980
    assert report["absolute"] == pytest.approx(20.0)
    assert report["relative_highs"] == pytest.approx(0.02)


def test_scip_divides_by_the_smaller_number_in_size():
    assert gap_report(1000.0, 980.0)["relative_scip"] == pytest.approx(20.0 / 980.0)
    assert gap_report(-50.0, -40.0)["relative_scip"] == pytest.approx(10.0 / 40.0)


def test_no_plan_means_no_gap():
    assert gap_report(math.inf, 950.0) == {"absolute": None, "relative_highs": None, "relative_scip": None}
    assert gap_report(-math.inf, 950.0)["absolute"] is None


def test_a_plan_with_no_proven_bound_has_an_infinite_gap():
    report = gap_report(950.0, math.inf)            # a plan worth 950, nothing proven about the best
    assert report == {"absolute": math.inf, "relative_highs": math.inf, "relative_scip": math.inf}
    assert gap_report(950.0, -math.inf)["absolute"] == math.inf


def test_a_zero_incumbent_has_no_relative_gap():
    report = gap_report(0.0, 5.0)
    assert report["absolute"] == pytest.approx(5.0)
    assert report["relative_highs"] is None
    assert report["relative_scip"] is None
