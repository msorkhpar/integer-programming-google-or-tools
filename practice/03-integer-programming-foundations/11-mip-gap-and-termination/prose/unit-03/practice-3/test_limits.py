import datetime

import pytest

from limits import limits_for


def request(**given):
    base = {"matters_dollars": None, "share_percent": None, "minutes": None, "nodes": None}
    return {**base, **given}


def test_a_request_in_dollars_percent_and_minutes_becomes_parameters():
    p = limits_for(request(matters_dollars=50_000, share_percent=0.5, minutes=30))
    assert p.absolute_gap_tolerance == pytest.approx(50.0)
    assert p.relative_gap_tolerance == pytest.approx(0.005)
    assert p.time_limit == datetime.timedelta(minutes=30)
    assert p.node_limit is None


def test_no_share_still_sets_the_relative_tolerance_to_zero():
    p = limits_for(request(matters_dollars=20_000, minutes=10))
    assert p.relative_gap_tolerance == 0.0
    assert p.absolute_gap_tolerance == pytest.approx(20.0)


def test_no_amount_leaves_the_absolute_tolerance_unset():
    p = limits_for(request(share_percent=1, minutes=10))
    assert p.absolute_gap_tolerance is None
    assert p.relative_gap_tolerance == pytest.approx(0.01)


def test_a_repeatable_request_uses_a_node_limit_and_no_time_limit():
    p = limits_for(request(share_percent=0.1, minutes=20, nodes=50_000))
    assert p.node_limit == 50_000
    assert p.time_limit is None
    assert p.relative_gap_tolerance == pytest.approx(0.001)


def test_half_a_minute_is_thirty_seconds():
    p = limits_for(request(share_percent=0.1, minutes=0.5))
    assert p.time_limit == datetime.timedelta(seconds=30)
