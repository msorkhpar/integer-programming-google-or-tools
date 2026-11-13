import pytest

from change import value_change

# A hospital's maintenance LP, swept over its equipment budget ($k): (from, to, price) segments.
SWEEP = [(0, 40, 3.0), (40, 70, 2.0), (70, 100, 0.5)]


def test_a_change_inside_one_segment_is_price_times_amount():
    assert value_change(SWEEP, 50, 10) == pytest.approx(20)
    assert value_change(SWEEP, 20, 15) == pytest.approx(45)


def test_a_change_across_a_breakpoint_uses_each_segments_price():
    assert value_change(SWEEP, 50, 30) == pytest.approx(20 * 2.0 + 10 * 0.5)


def test_a_cut_is_a_negative_change_priced_on_the_way_down():
    assert value_change(SWEEP, 50, -20) == pytest.approx(-(10 * 2.0 + 10 * 3.0))


def test_a_move_past_the_sweep_has_no_answer():
    assert value_change(SWEEP, 50, 60) is None
    assert value_change(SWEEP, 50, 45) == pytest.approx(20 * 2.0 + 25 * 0.5)
