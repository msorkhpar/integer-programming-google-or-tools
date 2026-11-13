from ortools.sat.python import cp_model

from vans import VanType, build

# A food bank's weekend drive, not the lesson's portfolio.
FLEET = [VanType("V1", 4, 300, 6, 2), VanType("V2", 10, 650, 3, 1), VanType("V3", 18, 1000, 4, 2)]
DEMAND, BUDGET, DRIVERS = 40, 4_000, 6


def allowed(counts: dict[str, int], budget: int = BUDGET, drivers: int = DRIVERS) -> bool:
    """Fix how many vans of each type are leased and ask CP-SAT whether every rule holds."""
    model, n = build(FLEET, DEMAND, budget, drivers)
    for name, var in n.items():
        model.add(var == counts.get(name, 0))
    return cp_model.CpSolver().solve(model) == cp_model.OPTIMAL


def test_the_fleet_must_carry_the_demand():
    # 2 x V2 + 2 x V3 carry 56 pallets; 2 x V1 + 3 x V2 carry 38, short of 40.
    assert allowed({"V2": 2, "V3": 2}) is True
    assert allowed({"V1": 2, "V2": 3}) is False


def test_the_fleet_must_fit_the_budget():
    # With $3,500: V2 + 2 x V3 costs 2,650; 3 x V2 + 2 x V3 costs 3,950.
    assert allowed({"V2": 1, "V3": 2}, budget=3_500) is True
    assert allowed({"V2": 3, "V3": 2}, budget=3_500) is False


def test_every_van_needs_a_driver():
    # 2 + 2 + 2 vans for 6 drivers is fine; 4 + 3 + 0 = 7 vans is one too many.
    assert allowed({"V1": 2, "V2": 2, "V3": 2}) is True
    assert allowed({"V1": 4, "V2": 3}) is False


def test_vans_come_in_whole_packs():
    # V3 is leased in packs of 2: 2 is a lease, 3 is not, though 3 x V3 meets every row.
    assert allowed({"V2": 1, "V3": 2}) is True
    assert allowed({"V3": 3}) is False


def test_no_more_vans_than_the_dealer_has():
    # V1: 6 available. With 20 drivers, 6 x V1 + 2 x V2 is a lease; 8 x V1 + V2 is not.
    assert allowed({"V1": 6, "V2": 2}, drivers=20) is True
    assert allowed({"V1": 8, "V2": 1}, drivers=20) is False
