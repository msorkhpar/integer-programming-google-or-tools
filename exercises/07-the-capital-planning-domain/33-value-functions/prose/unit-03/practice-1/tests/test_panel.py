import pytest

from panel import panel_weights, price

# A water utility's board: breaks avoided, leakage avoided (megalitres), savings ($k).
REFERENCE = {"breaks": 20, "leakage": 500, "savings": 1_000}


def test_the_settled_ratings_become_weights_that_sum_to_one():
    votes = {"breaks": [100, 100, 100], "leakage": [60, 80, 100], "savings": [50, 40, 60]}
    w = panel_weights(votes)                                  # settled 100, 80, 50 of 230
    assert w == pytest.approx({"breaks": 100 / 230, "leakage": 80 / 230, "savings": 50 / 230})


def test_a_price_is_the_ratio_of_values_per_unit():
    w = {"breaks": 0.5, "leakage": 0.3, "savings": 0.2}
    assert price(w, REFERENCE, "breaks", "savings") == pytest.approx(125.0)      # (0.5/20) / (0.2/1000)
    assert price(w, REFERENCE, "leakage", "savings") == pytest.approx(3.0)
    assert price(w, REFERENCE, "savings", "savings") == pytest.approx(1.0)


def test_one_extreme_vote_does_not_drag_the_settled_rating():
    votes = {"breaks": [100, 100, 100], "leakage": [90, 100, 10], "savings": [50, 50, 50]}
    w = panel_weights(votes)                                  # settled 100, 90, 50 of 240
    assert w["leakage"] == pytest.approx(90 / 240)


def test_an_even_panel_settles_halfway_between_its_middle_votes():
    votes = {"breaks": [100, 100, 100, 100], "leakage": [40, 90, 70, 60], "savings": [50, 50, 50, 50]}
    w = panel_weights(votes)                                  # settled 100, 65, 50 of 215
    assert w["leakage"] == pytest.approx(65 / 215)
