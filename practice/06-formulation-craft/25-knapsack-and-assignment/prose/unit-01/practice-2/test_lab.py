from ortools.math_opt.python import mathopt

from lab import Analyzer, build

# A hospital laboratory's candidate analyzers, not the lesson's portfolio.
LAB = [Analyzer("A", 500, 200, 8.0, 4.0), Analyzer("B", 300, 150, 6.0, 6.0), Analyzer("C", 700, 260, 10.0, 3.0),
       Analyzer("D", 200, 90, 4.0, 2.0), Analyzer("E", 400, 120, 5.0, 9.0)]
FLOOR, POWER, RATE, MAX_LEASE = 20.0, 15.0, 10.0, 6.0


def allowed(plan: set[str], budget: int) -> bool:
    """Fix which analyzers are bought and ask whether some lease makes the plan fit."""
    model, x = build(LAB, budget, FLOOR, POWER, RATE, MAX_LEASE)
    for aid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if aid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_power_limits_the_plan_whatever_the_money():
    # A + C + D: 9 kW. B + E: 15 kW is the limit; A + B + E: 19 kW is over it.
    assert allowed({"A", "C", "D"}, budget=10_000) is True
    assert allowed({"A", "B", "E"}, budget=10_000) is False


def test_the_budget_pays_for_the_analyzers_and_the_lease():
    # A + C: 18 m^2, no lease, 460. A + B + C: 24 m^2, lease 4 m^2 for 40, 610 + 40 = 650.
    assert allowed({"A", "C"}, budget=460) is True
    assert allowed({"A", "B", "C"}, budget=650) is True
    assert allowed({"A", "B", "C"}, budget=640) is False


def test_leased_space_has_a_limit():
    # A + B + C + D: 28 m^2 needs 8 m^2 leased; at most 6 may be leased.
    assert allowed({"A", "C", "D"}, budget=10_000) is True
    assert allowed({"A", "B", "C", "D"}, budget=10_000) is False


def test_space_may_be_leased_in_part_of_a_square_metre():
    # Two analyzers of 10.5 and 10.0 m^2 need 0.5 m^2 leased, for 5: 200 + 5 = 205.
    pair = [Analyzer("P", 1, 100, 10.5, 1.0), Analyzer("Q", 1, 100, 10.0, 1.0)]

    def both_fit(budget: int) -> bool:
        model, x = build(pair, budget, FLOOR, POWER, RATE, MAX_LEASE)
        for var in x.values():
            var.lower_bound = var.upper_bound = 1.0
        return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL

    assert both_fit(205) is True
    assert both_fit(204) is False
