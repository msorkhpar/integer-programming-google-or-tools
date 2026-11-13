from depots import Upgrade, weighted_choice

CITY = [
    Upgrade("U1", 4, 300, 2000),
    Upgrade("U2", 3, 100, 9000),
    Upgrade("U3", 3, 250, 1000),
    Upgrade("U4", 2, 60, 5000),
]


def test_a_plan_best_on_both_measures_is_chosen():
    small = [Upgrade("V1", 5, 400, 6000), Upgrade("V2", 5, 100, 1000), Upgrade("V3", 5, 50, 500)]
    assert weighted_choice(small, 5, 30) == {"V1"}
    assert weighted_choice(small, 10, 30) == {"V1", "V2"}


def test_the_price_is_per_tonne_not_per_kilogram():
    # at 20 riders a tonne: U2+U3 is worth 550, U1+U4 500, U2+U4 440
    assert weighted_choice(CITY, 6, 20) == {"U2", "U3"}


def test_the_price_multiplies_the_co2_not_the_riders():
    # at 50 riders a tonne: U2+U4 is worth 860, U2+U3 850, U1+U4 710
    assert weighted_choice(CITY, 6, 50) == {"U2", "U4"}
