import pytest

from overtime import plan

# A rail depot's overhaul jobs: name -> (hours, value $). Not the lesson's portfolio.
JOBS = {"bogie": (30, 2400), "brakes": (20, 1500), "doors": (25, 1200), "hvac": (15, 600), "paint": (10, 300)}
HOURS = [0, 10, 20, 40]
RISING = [0, 400, 1000, 2600]        # $40, $60, then $80 an hour
DISCOUNT = [0, 700, 1200, 1800]      # $70, $50, then $30 an hour


def run(*args):
    try:
        return plan(*args)
    except Exception as error:
        raise AssertionError(f"plan raised {type(error).__name__}: {error}") from None


def on_curve(hours, cost, h):
    for (a, fa), (b, fb) in zip(zip(hours, cost), zip(hours[1:], cost[1:])):
        if h <= b + 1e-9:
            return fa + (fb - fa) * (h - a) / (b - a)


def test_rising_overtime_prices_with_a_full_week():
    net, over, pay = run(JOBS, 60, HOURS, RISING)
    assert net == pytest.approx(4400)
    assert pay == pytest.approx(on_curve(HOURS, RISING, over))


def test_rising_overtime_prices_with_a_short_week():
    net, over, pay = run(JOBS, 45, HOURS, RISING)
    assert net == pytest.approx(3700)
    assert pay == pytest.approx(on_curve(HOURS, RISING, over))


def test_a_volume_discount_is_paid_at_its_true_price():
    net, over, pay = run(JOBS, 45, HOURS, DISCOUNT)
    assert pay == pytest.approx(on_curve(HOURS, DISCOUNT, over))
    assert net == pytest.approx(3600)
