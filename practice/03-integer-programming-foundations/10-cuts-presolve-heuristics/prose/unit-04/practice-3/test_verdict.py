import pytest

from verdict import verdict


def test_a_gap_under_the_tolerance():
    gap, ok = verdict(1000.0, 1000.5, 1e-3, "max", False)
    assert gap == pytest.approx(0.0005) and ok is True


def test_a_gap_over_the_tolerance():
    gap, ok = verdict(500.0, 501.0, 1e-3, "max", False)
    assert gap == pytest.approx(0.002) and ok is False


def test_an_integral_objective_rounds_a_maximization_bound_down():
    gap, ok = verdict(41000, 41004.6, 1e-4, "max", True)
    assert gap == pytest.approx(4 / 41000) and ok is True


def test_an_integral_objective_rounds_a_minimization_bound_up():
    gap, ok = verdict(41000, 40995.4, 1e-4, "min", True)
    assert gap == pytest.approx(4 / 41000) and ok is True
