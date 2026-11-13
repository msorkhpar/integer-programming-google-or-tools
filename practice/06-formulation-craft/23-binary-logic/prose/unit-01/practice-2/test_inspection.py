from ortools.math_opt.python import mathopt

from inspection import Pipe, build

# A water utility's trunk mains, not the lesson's portfolio.
MAINS = [Pipe("A", 20.0, 100), Pipe("B", 15.0, 80), Pipe("C", 25.0, 60), Pipe("D", 12.0, 40),
         Pipe("E", 5.0, 30), Pipe("F", 28.0, 20)]
KM_PER_WEEK, RATE, MAX_WEEKS = 30.0, 50, 3


def allowed(plan: set[str], budget: int) -> bool:
    """Fix which mains are inspected and ask whether some rental makes the plan affordable."""
    model, x = build(MAINS, KM_PER_WEEK, RATE, MAX_WEEKS, budget)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_the_rental_is_paid_from_the_budget():
    # A + B: 35 km, two weeks, 180 + 100 = 280. A to D: 72 km, three weeks, 280 + 150 = 430.
    assert allowed({"A", "B"}, budget=300) is True
    assert allowed({"A", "B", "C", "D"}, budget=300) is False


def test_the_robot_is_available_for_a_limited_number_of_weeks():
    # Every main: 105 km, more than three weeks can inspect, whatever the budget.
    assert allowed({"A", "B", "C", "D"}, budget=100_000) is True
    assert allowed({"A", "B", "C", "D", "E", "F"}, budget=100_000) is False


def test_weeks_are_rented_whole():
    # A + C: 45 km, two weeks, 160 + 100 = 260. A + B + D: 47 km, two weeks, 220 + 100 = 320.
    assert allowed({"A", "C"}, budget=300) is True
    assert allowed({"A", "B", "D"}, budget=300) is False


def test_a_plan_with_no_pipes_rents_no_weeks():
    assert allowed(set(), budget=30) is True
    assert allowed({"E"}, budget=30) is False
