import pytest

from feeders import Feeder, consequence, saidi_minutes


def test_one_class_of_customers_and_no_switching():
    f = Feeder(2_000, 0, 0.0, 1.0, 5.0, 0.03, 0.4, 120)
    assert consequence(f) == pytest.approx(120 + 2_000 * 5.0 * 0.03)


def test_critical_customers_are_priced_at_their_own_rate():
    f = Feeder(1_000, 20, 0.0, 1.0, 4.0, 0.02, 0.5, 100)
    assert consequence(f) == pytest.approx(100 + (1_000 * 0.02 + 20 * 0.5) * 4.0)


def test_switched_customers_wait_only_until_the_switching():
    f = Feeder(3_000, 0, 0.75, 2.0, 10.0, 0.01, 0.4, 200)
    assert consequence(f) == pytest.approx(200 + 3_000 * 0.01 * (0.75 * 2.0 + 0.25 * 10.0))


def test_saidi_counts_minutes_per_customer_served():
    f = Feeder(1_500, 50, 0.4, 1.0, 6.0, 0.02, 0.3, 90)
    hours = 0.4 * 1.0 + 0.6 * 6.0
    assert saidi_minutes(f, 60_000) == pytest.approx(1_550 * hours * 60 / 60_000)
