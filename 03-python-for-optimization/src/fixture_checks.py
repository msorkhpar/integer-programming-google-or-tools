"""Tests of GridCap's tiny portfolio that share one fixture; run this file to run them."""

import os
from pathlib import Path

import pytest
from pytest import approx

from gridcap import Portfolio, generate, load_csv, save_csv


@pytest.fixture(scope="module")
def tiny() -> Portfolio:
    return generate("tiny")


def test_capex_is_the_sum_of_the_cost_profile(tiny):
    assert tiny.project("P003").capex == 980 + 1490


def test_present_value_of_a_one_year_project(tiny):
    p001 = tiny.project("P001")
    years = p001.earliest_start - tiny.years[0]
    assert p001.capex / (1 + tiny.discount_rate) ** years == approx(2009.3458, rel=1e-6)


def test_csv_round_trip_keeps_the_portfolio(tiny, tmp_path):
    assert load_csv(save_csv(tiny, tmp_path)).content_hash() == tiny.content_hash()


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    raise SystemExit(pytest.main(["-q", "--setup-show", "-p", "no:cacheprovider", "--rootdir", ".", Path(__file__).name]))
