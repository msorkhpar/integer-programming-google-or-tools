"""Two tests of one present value: the first compares floats with ==, the second with a tolerance."""

import os
from pathlib import Path

import pytest
from pytest import approx

RATE = 0.07


def present_value(cost: int, years_ahead: int) -> float:
    """What `cost` paid `years_ahead` years from now is worth today, at RATE a year."""
    return cost / (1 + RATE) ** years_ahead


def test_present_value_exact():
    assert present_value(2150, 1) == 2150 * (1 + RATE) ** -1


def test_present_value_within_tolerance():
    assert present_value(2150, 1) == approx(2150 * (1 + RATE) ** -1)


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    code = pytest.main(["-q", "--tb=short", "-p", "no:cacheprovider", "--rootdir", ".", Path(__file__).name])
    print("pytest exit code:", int(code))
