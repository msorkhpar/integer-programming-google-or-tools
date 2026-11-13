import pytest

from bounds import Asset, lp_bounds

# Two fleets of substation transformers, not the lesson's portfolio. Costs in $k, ratings in MVA.
TOWN = {"T1": Asset(120, 400, 30, 60), "T2": Asset(90, 350, 25, 50),
        "T3": Asset(150, 500, 40, 75), "T4": Asset(60, 260, 20, 35)}
CITY = {"S1": Asset(200, 900, 45, 90), "S2": Asset(300, 2500, 60, 140), "S3": Asset(80, 300, 20, 40)}


def run(assets, demand):
    try:
        return lp_bounds(assets, demand)
    except Exception as error:
        raise AssertionError(f"lp_bounds raised {type(error).__name__}: {error}") from None


def test_the_bounds_sit_below_the_town_optimum_in_order():
    big_m, hull = run(TOWN, 150)
    assert big_m <= hull + 1e-6 and hull <= 770 + 1e-6          # 770: the MILP optimum
    assert hull >= 420 - 1e-6                                    # 420: every transformer at least repaired


def test_the_bounds_sit_below_the_city_optimum_in_order():
    big_m, hull = run(CITY, 200)
    assert big_m <= hull + 1e-6 and hull <= 2780 + 1e-6
    assert hull >= 580 - 1e-6


def test_the_bounds_are_lp_values_not_the_milp_optimum():
    assert run(TOWN, 150) == pytest.approx((489.018, 750.0), abs=1e-3)
    assert run(CITY, 150) == pytest.approx((555.195, 877.778), abs=1e-3)
