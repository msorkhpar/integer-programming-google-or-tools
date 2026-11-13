import pytest

from flow import ship

DIRECT = {("W1", "P1"): (2, 100), ("W1", "P2"): (4, 100), ("W1", "P3"): (5, 100),
          ("W2", "P2"): (3, 100), ("W2", "P3"): (2, 100)}
DEMAND = {"P1": 30, "P2": 25, "P3": 35}


def test_the_cheapest_shipments_meet_every_pantry():
    status, cost, flows = ship({"W1": 50, "W2": 40}, DEMAND, DIRECT)
    assert status == "OPTIMAL"
    assert cost == pytest.approx(225)
    assert flows[("W2", "P3")] == pytest.approx(35)
    assert flows[("W1", "P2")] == pytest.approx(20)


def test_a_warehouse_may_keep_what_no_pantry_needs():
    status, cost, flows = ship({"W1": 70, "W2": 40}, DEMAND, DIRECT)
    assert status == "OPTIMAL"
    assert cost == pytest.approx(225)


def test_no_route_carries_more_than_its_capacity():
    status, cost, flows = ship({"W1": 50, "W2": 40}, DEMAND, {**DIRECT, ("W2", "P3"): (2, 20)})
    assert status == "OPTIMAL"
    assert flows[("W2", "P3")] <= 20 + 1e-6
    assert cost == pytest.approx(255)


def test_a_sorting_hub_sends_out_exactly_what_it_receives():
    arcs = {("W1", "P1"): (5, 40), ("W1", "H"): (2, 50), ("W2", "P3"): (6, 30), ("W2", "H"): (1, 40),
            ("H", "P1"): (2, 50), ("H", "P2"): (3, 50), ("H", "P3"): (2, 50)}
    status, cost, flows = ship({"W1": 50, "W2": 40}, {"P1": 30, "P2": 25, "P3": 20}, arcs)
    assert status == "OPTIMAL"
    into = flows[("W1", "H")] + flows[("W2", "H")]
    out = flows[("H", "P1")] + flows[("H", "P2")] + flows[("H", "P3")]
    assert into == pytest.approx(out)
    assert cost == pytest.approx(285)


def test_more_demand_than_supply_gives_infeasible_with_no_answer():
    assert ship({"W1": 50, "W2": 40}, {"P1": 30, "P2": 25, "P3": 45}, DIRECT) == ("INFEASIBLE", None, None)
