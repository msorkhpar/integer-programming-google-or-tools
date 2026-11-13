import pytest

from stops import rank, score

REFERENCE = {"time": (500, "hours"), "complaints": (40, "complaints"), "savings": (200, "$k")}
WEIGHTS = {"time": 0.5, "complaints": 0.2, "savings": 0.3}

# Rider time saved, complaints avoided and operating savings for four bus-stop upgrades.
STOPS = {
    "Ash": {"time": (250, "hours"), "complaints": (4, "complaints"), "savings": (20, "$k")},        # 0.25+0.02+0.03
    "Birch": {"time": (100, "hours"), "complaints": (20, "complaints"), "savings": (100, "$k")},    # 0.10+0.10+0.15
    "Cedar": {"time": (50, "hours"), "complaints": (2, "complaints"), "savings": (180, "$k")},      # 0.05+0.01+0.27
    "Dogwood": {"time": (10, "hours"), "complaints": (8, "complaints"), "savings": (10, "$k")},     # 0.01+0.04+0.015
}


def test_a_score_is_the_weighted_share_of_each_reference():
    assert score(STOPS["Birch"], REFERENCE, WEIGHTS) == pytest.approx(0.35)
    assert score(STOPS["Cedar"], REFERENCE, WEIGHTS) == pytest.approx(0.33)


def test_projects_rank_from_the_highest_score():
    assert rank(STOPS, REFERENCE, WEIGHTS) == ["Birch", "Cedar", "Ash", "Dogwood"]


def test_a_benefit_recorded_in_another_unit_scores_the_same():
    in_minutes = {**STOPS["Ash"], "time": (15_000, "minutes")}
    in_dollars = {**STOPS["Ash"], "savings": (20_000, "$")}
    assert score(in_minutes, REFERENCE, WEIGHTS) == pytest.approx(0.30)
    assert score(in_dollars, REFERENCE, WEIGHTS) == pytest.approx(0.30)


def test_a_reference_stated_in_another_unit_changes_nothing():
    restated = {"time": (30_000, "minutes"), "complaints": (40 / 12, "dozen complaints"), "savings": (200_000, "$")}
    assert rank(STOPS, restated, WEIGHTS) == ["Birch", "Cedar", "Ash", "Dogwood"]
    assert score(STOPS["Cedar"], restated, WEIGHTS) == pytest.approx(0.33)


def test_equal_scores_are_listed_in_name_order():
    twins = {"Fir": STOPS["Ash"], "Elm": STOPS["Ash"], "Birch": STOPS["Birch"]}
    assert rank(twins, REFERENCE, WEIGHTS) == ["Birch", "Elm", "Fir"]
