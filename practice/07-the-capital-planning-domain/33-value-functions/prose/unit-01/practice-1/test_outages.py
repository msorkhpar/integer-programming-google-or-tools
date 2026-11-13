import pytest

from outages import Step, indices

SERVED = 10_000


def test_each_step_counts_at_its_own_restoration_time():
    got = indices([[Step(600, 30), Step(400, 90)]], SERVED)       # 1,000 out; 18,000 + 36,000 minutes
    assert got["SAIFI"] == pytest.approx(0.1)
    assert got["SAIDI"] == pytest.approx(5.4)
    assert got["CAIDI"] == pytest.approx(54.0)


def test_a_year_of_outages_adds_up():
    year = [[Step(600, 20), Step(400, 70)], [Step(200, 40)], [Step(1_000, 10), Step(800, 77.5)]]
    got = indices(year, SERVED)                    # 3,000 interruptions, 120,000 customer-minutes
    assert got["SAIFI"] == pytest.approx(0.3)
    assert got["SAIDI"] == pytest.approx(12.0)
    assert got["CAIDI"] == pytest.approx(40.0)


def test_customers_back_within_five_minutes_do_not_count():
    got = indices([[Step(500, 3), Step(500, 60)]], SERVED)        # the first 500 were a blink
    assert got["SAIFI"] == pytest.approx(0.05)
    assert got["SAIDI"] == pytest.approx(3.0)


def test_exactly_five_minutes_is_still_momentary():
    got = indices([[Step(300, 5), Step(200, 20)]], SERVED)
    assert got["SAIFI"] == pytest.approx(0.02)
    assert got["CAIDI"] == pytest.approx(20.0)


def test_caidi_weights_every_customer_not_every_outage():
    got = indices([[Step(100, 10)], [Step(900, 60)]], SERVED)    # 55,000 minutes over 1,000 customers
    assert got["CAIDI"] == pytest.approx(55.0)
    assert indices([[Step(5_000, 2)]], SERVED) == {"SAIFI": 0.0, "SAIDI": 0.0, "CAIDI": 0.0}
