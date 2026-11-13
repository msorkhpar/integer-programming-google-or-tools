import math

import pytest

from pumps import Asset, Project, most_risk_removed, risk_avoided


def next_year(age: float, beta: float, eta: float) -> float:
    def failed_by(t: float) -> float:
        return 1 - math.exp(-((t / eta) ** beta))
    return (failed_by(age + 1) - failed_by(age)) / (1 - failed_by(age))


ASSETS = {
    "A": Asset(age=28, cof=1200, beta=3.0, eta=35),
    "B": Asset(age=45, cof=800, beta=2.5, eta=50),
    "C": Asset(age=12, cof=1500, beta=3.5, eta=30),
    "D": Asset(age=60, cof=400, beta=2.0, eta=55),
}

#: One replacement per pump station; R3 is ordered by the regulator.
SIMPLE = [
    Project("R1", "A", "replace", 500),
    Project("R2", "B", "replace", 450),
    Project("R3", "C", "replace", 200, must_do=True),
    Project("R4", "D", "replace", 300),
]

#: A replacement and a cheaper repair for stations A and D; at most one project per station.
CHOICES = [
    Project("P1", "A", "replace", 500),
    Project("P2", "A", "repair", 120),
    Project("P3", "B", "replace", 450),
    Project("P4", "C", "repair", 90, must_do=True),
    Project("P5", "D", "replace", 300),
    Project("P6", "D", "repair", 60),
]


def test_a_replacement_removes_the_risk_of_its_age_less_the_risk_of_a_new_asset():
    a = ASSETS["B"]
    expected = a.cof * (next_year(45, a.beta, a.eta) - next_year(0, a.beta, a.eta))
    assert risk_avoided(Project("X", "B", "replace", 1), ASSETS) == pytest.approx(expected, rel=1e-9)


def test_a_repair_leaves_the_asset_at_half_its_age():
    a = ASSETS["A"]
    expected = a.cof * (next_year(28, a.beta, a.eta) - next_year(14, a.beta, a.eta))
    assert risk_avoided(Project("X", "A", "repair", 1), ASSETS) == pytest.approx(expected, rel=1e-9)


def test_the_plan_removes_the_most_risk_the_budget_and_the_must_do_allow():
    total, plan = most_risk_removed(SIMPLE, ASSETS, 700)
    assert plan == {"R1", "R3"} and total == pytest.approx(85.7704, abs=1e-3)
    total, plan = most_risk_removed(SIMPLE, ASSETS, 1000)
    assert plan == {"R1", "R3", "R4"} and total == pytest.approx(101.3224, abs=1e-3)


def test_the_best_plan_is_not_the_riskiest_projects_first():
    # Funding the biggest risk first (P1) leaves too little for the pair that removes more.
    total, plan = most_risk_removed(CHOICES, ASSETS, 700)
    assert plan == {"P2", "P3", "P4"} and total == pytest.approx(98.3798, abs=1e-3)


def test_a_station_is_never_both_replaced_and_repaired():
    total, plan = most_risk_removed(CHOICES, ASSETS, 1100)
    assert plan == {"P1", "P3", "P4", "P6"} and total == pytest.approx(123.5820, abs=1e-3)
