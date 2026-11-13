import pytest

from allowance import allowed_overrun


def test_an_absolute_tolerance_is_worth_one_unit_of_the_row_times_the_tolerance():
    assert allowed_overrun(3_000_000, 1_000, 1e-6, relative=False) == pytest.approx(0.001)
    assert allowed_overrun(3_000_000, 1_000_000_000, 1e-6, relative=False) == pytest.approx(1_000)


def test_a_relative_tolerance_grows_with_the_rows_size():
    assert allowed_overrun(3_000_000, 1_000, 1e-6, relative=True) == pytest.approx(3.0)
    assert allowed_overrun(3_000_000, 1_000_000, 1e-6, relative=True) == pytest.approx(3.0)


def test_a_relative_tolerance_never_drops_below_the_absolute_one():
    assert allowed_overrun(3_000_000, 1_000_000_000, 1e-6, relative=True) == pytest.approx(1_000)
    assert allowed_overrun(400, 1_000, 1e-6, relative=True) == pytest.approx(0.001)


def test_a_row_with_a_negative_side_uses_its_size():
    assert allowed_overrun(-3_000_000, 1_000, 1e-6, relative=True) == pytest.approx(3.0)
    assert allowed_overrun(-3_000_000, 1_000, 1e-6, relative=False) == pytest.approx(0.001)
