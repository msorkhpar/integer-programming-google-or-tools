from ortools.math_opt.python import mathopt

from loading import Order, Truck, build

# A utility warehouse's material orders for tomorrow, not the lesson's portfolio.
ORDERS = [Order("A", 5, 800, 2.0), Order("B", 4, 600, 3.5), Order("C", 3, 500, 1.0),
          Order("D", 6, 900, 1.5, site="North"), Order("E", 2, 300, 0.5, site="North"), Order("F", 1, 200, 2.5)]
TRUCKS = [Truck("T1", 1500, 4.0), Truck("T2", 1200, 5.0)]


def allowed(loads: dict[str, str]) -> bool:
    """loads: order -> truck it travels on; orders left out wait. Asks the solver whether the rules allow it."""
    model, x = build(ORDERS, TRUCKS)
    for (oid, tid), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if loads.get(oid) == tid else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed_pairs(pairs: set[tuple[str, str]]) -> bool:
    model, x = build(ORDERS, TRUCKS)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in pairs else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_each_truck_keeps_its_weight_and_its_volume():
    # T1: A + C = 1,300 kg, 3.0 m3. T2: B + F = 800 kg, 6.0 m3, over T2's volume though light.
    assert allowed({"A": "T1", "C": "T1", "B": "T2"}) is True
    assert allowed({"A": "T1", "C": "T1", "B": "T2", "F": "T2"}) is False
    # T1: A + B = 1,400 kg but 5.5 m3, over T1's volume.
    assert allowed({"A": "T1", "B": "T1"}) is False
    # T1: A + D + E = 4.0 m3, exactly T1's volume, but 2,000 kg, over its weight.
    assert allowed({"A": "T1", "D": "T1", "E": "T1"}) is False


def test_an_order_travels_on_one_truck_at_most():
    assert allowed_pairs({("C", "T1")}) is True
    assert allowed_pairs({("C", "T1"), ("C", "T2")}) is False


def test_a_sites_orders_ride_the_same_truck():
    # D and E together on T2: 1,200 kg, 2.0 m3. D on T1 and E on T2: split.
    assert allowed({"D": "T2", "E": "T2"}) is True
    assert allowed({"D": "T1", "E": "T2"}) is False


def test_a_sites_orders_wait_together():
    # Both wait: fine. E ships while D waits: refused.
    assert allowed({"A": "T1"}) is True
    assert allowed({"E": "T1"}) is False
