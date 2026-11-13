import pulp

from refurbish import Station, build, refurbish

# A water utility's pump stations, not the lesson's portfolio.
WEST = [
    Station("S1", 50, 40, 4),
    Station("S2", 45, 35, 3),
    Station("S3", 30, 30, 5),
    Station("S4", 12, 20, 2, must=True),
    Station("S5", 25, 25, 3),
]


def row_names(prob) -> set[str]:
    return {row.name for row in prob.constraints()}


def test_best_plan_within_the_budget():
    assert refurbish(WEST, budget=80, crew_days=100, bypass_pairs=[("S1", "S2")]) == (82, ["S2", "S4", "S5"])


def test_rows_carry_the_formulation_labels():
    prob, y = build(WEST, budget=80, crew_days=100, bypass_pairs=[("S1", "S2")])
    assert row_names(prob) == {"budget", "crew", "bypass_S1_S2", "must_S4"}
    assert set(y) == {"S1", "S2", "S3", "S4", "S5"}


def test_crew_days_not_stations_are_counted():
    east = [Station("A", 10, 1, 6), Station("B", 9, 1, 1), Station("C", 8, 1, 1), Station("D", 7, 1, 1)]
    assert refurbish(east, budget=100, crew_days=6, bypass_pairs=[]) == (24, ["B", "C", "D"])


def test_a_station_in_two_bypass_pairs_gets_a_row_for_each():
    chain = [Station("P1", 5, 1, 1), Station("P2", 9, 1, 1), Station("P3", 5, 1, 1)]
    assert refurbish(chain, budget=100, crew_days=100, bypass_pairs=[("P1", "P2"), ("P2", "P3")]) == (10, ["P1", "P3"])


def test_a_must_station_is_refurbished_even_when_others_save_more():
    pair = [Station("M", 1, 50, 1, must=True), Station("N", 20, 50, 1)]
    assert refurbish(pair, budget=60, crew_days=100, bypass_pairs=[]) == (1, ["M"])
