import pytest

from shares import share_range

FLEET = [(0, 10), (6, 8), (10, 0)]


def test_a_middle_option_holds_between_two_break_even_shares():
    assert share_range(FLEET, 1) == pytest.approx((0.25, 2 / 3))


def test_an_end_option_holds_from_the_end_of_the_scale():
    assert share_range(FLEET, 0) == pytest.approx((0.0, 0.25))
    assert share_range(FLEET, 2) == pytest.approx((2 / 3, 1.0))


def test_an_option_no_share_picks_has_no_range():
    assert share_range([(0, 10), (4, 5), (10, 0)], 1) is None
    assert share_range(FLEET + [(5, 7)], 3) is None


def test_an_identical_option_shares_the_range():
    assert share_range([(0, 10), (6, 8), (6, 8), (10, 0)], 1) == pytest.approx((0.25, 2 / 3))
