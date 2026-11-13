import pytest

from what_if import build, what_if


def test_a_small_cut_is_predicted_exactly():
    model, budget = build()
    predicted, actual = what_if(model, budget, 1)
    assert actual == pytest.approx(51)
    assert predicted == pytest.approx(actual)


def test_a_large_cut_is_missed_by_the_dual_prediction():
    model, budget = build()
    predicted, actual = what_if(model, budget, 6)
    assert actual == pytest.approx(39)
    assert predicted != pytest.approx(actual)


def test_the_prediction_uses_the_dual_value_of_the_base_solve():
    model, budget = build()
    predicted, _ = what_if(model, budget, 6)
    assert predicted == pytest.approx(53 - 2 * 6)


def test_the_model_is_left_as_given():
    model, budget = build()
    what_if(model, budget, 6)
    assert budget.upper_bound == 20
    assert what_if(model, budget, 1) == (pytest.approx(51), pytest.approx(51))
