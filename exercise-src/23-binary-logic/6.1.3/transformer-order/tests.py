from ortools.math_opt.python import mathopt

from order import Project, build

# A municipal utility's projects, not the lesson's portfolio.
PROJECTS = [Project("P1", 6, 50), Project("P2", 5, 40), Project("P3", 4, 30), Project("P4", 12, 90),
            Project("P5", 15, 100), Project("P6", 0, 25)]
MIN_ORDER, MAX_ORDER, FEE = 10, 30, 20


def allowed(plan: set[str], budget: int = 10_000) -> bool:
    """Fix which projects are funded and ask whether the model accepts the plan."""
    model, x = build(PROJECTS, MIN_ORDER, MAX_ORDER, FEE, budget)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_an_order_must_reach_the_minimum():
    assert allowed({"P1", "P2"}) is True                  # 11 units
    assert allowed({"P1"}) is False                       # 6 units


def test_an_order_may_not_exceed_the_maximum():
    assert allowed({"P4", "P5"}) is True                  # 27 units
    assert allowed({"P3", "P4", "P5"}) is False           # 31 units


def test_the_delivery_fee_is_paid_from_the_budget():
    assert allowed({"P1", "P3"}, budget=105) is True      # 10 units: 80 + 20 = 100
    assert allowed({"P1", "P2"}, budget=105) is False     # 11 units: 90 + 20 = 110


def test_a_plan_with_no_transformers_places_no_order():
    assert allowed(set(), budget=10) is True
    assert allowed({"P3"}, budget=10) is False


def test_projects_that_need_no_transformer_do_not_trigger_an_order():
    assert allowed({"P6"}) is True                        # 0 units
    assert allowed({"P3", "P6"}) is False                 # 4 units
