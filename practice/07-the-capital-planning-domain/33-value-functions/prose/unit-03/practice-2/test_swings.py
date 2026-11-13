import pytest

from swings import price, rerate

# A bus operator: rider-hours saved, accidents avoided, savings ($k).
OLD = {"riders": 2_000, "accidents": 2, "savings": 500}
RATINGS = {"riders": 100, "accidents": 50, "savings": 20}
PROJECTS = {
    "Lane A": {"riders": 1_500, "accidents": 0.2, "savings": 100},
    "Lane B": {"riders": 300, "accidents": 1.5, "savings": 50},
    "Depot": {"riders": 0, "accidents": 0.1, "savings": 480},
    "Signals": {"riders": 900, "accidents": 0.9, "savings": 0},
}


def order(ratings, reference):
    total = sum(ratings.values())
    value = {p: sum(ratings[m] / total * b[m] / reference[m] for m in b) for p, b in PROJECTS.items()}
    return sorted(value, key=lambda p: -value[p])


def test_a_wider_swing_gets_a_proportionally_bigger_rating():
    assert rerate(RATINGS, OLD, {**OLD, "accidents": 4}) == pytest.approx({"riders": 100, "accidents": 100, "savings": 20})
    assert rerate(RATINGS, OLD, {**OLD, "savings": 250}) == pytest.approx({"riders": 100, "accidents": 50, "savings": 10})


def test_every_price_is_kept():
    new = {"riders": 3_000, "accidents": 1, "savings": 400}
    again = rerate(RATINGS, OLD, new)
    for m in ("riders", "accidents"):
        assert price(again, new, m, "savings") == pytest.approx(price(RATINGS, OLD, m, "savings"))


def test_the_projects_keep_their_order():
    new = {"riders": 6_000, "accidents": 1, "savings": 600}
    assert order(rerate(RATINGS, OLD, new), new) == order(RATINGS, OLD)
    assert order(RATINGS, new) != order(RATINGS, OLD)        # without re-rating, the order moves


def test_the_biggest_swing_is_rated_100_again():
    again = rerate(RATINGS, OLD, {**OLD, "riders": 500})      # riders' swing shrinks to a quarter
    assert again == pytest.approx({"riders": 50, "accidents": 100, "savings": 40})
