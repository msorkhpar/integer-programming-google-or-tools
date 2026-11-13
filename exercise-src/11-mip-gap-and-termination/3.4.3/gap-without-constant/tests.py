import math

import pytest

from true_gap import true_gap


def test_a_large_constant_hides_most_of_the_gap():
    got = true_gap(incumbent=2_224_000, bound=2_224_200, constant=2_000_000)
    assert got == {"absolute": pytest.approx(200), "seen": pytest.approx(200 / 2_224_000),
                   "on_decisions": pytest.approx(200 / 224_000)}


def test_with_no_constant_both_gaps_agree():
    got = true_gap(incumbent=5_000, bound=5_050, constant=0)
    assert got == {"absolute": pytest.approx(50), "seen": pytest.approx(0.01), "on_decisions": pytest.approx(0.01)}


def test_a_minimization_gives_positive_gaps():
    got = true_gap(incumbent=40_500, bound=40_100, constant=40_000)
    assert got == {"absolute": pytest.approx(400), "seen": pytest.approx(400 / 40_500),
                   "on_decisions": pytest.approx(0.8)}


def test_a_negative_constant_is_removed_by_subtracting_it():
    got = true_gap(incumbent=1_500, bound=1_600, constant=-500)
    assert got == {"absolute": pytest.approx(100), "seen": pytest.approx(100 / 1_500),
                   "on_decisions": pytest.approx(0.05)}


def test_decisions_worth_nothing_give_an_infinite_gap():
    got = true_gap(incumbent=1_000_000, bound=1_000_050, constant=1_000_000)
    assert got == {"absolute": pytest.approx(50), "seen": pytest.approx(50 / 1_000_000), "on_decisions": math.inf}
