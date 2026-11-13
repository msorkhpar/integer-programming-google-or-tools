from ortools.math_opt.python import mathopt

from repairs import Repair, build

# A gas utility's leak repairs, not the lessons' portfolio.
REPAIRS = [
    Repair("L1", 40, 30, 10),
    Repair("L2", 30, 25, 10),
    Repair("L3", 50, 10, 30, main="M1"),
    Repair("L4", 20, 5, 18, main="M1"),
    Repair("L5", 30, 20, 5),
]
BUDGET, FLOOR = 100, 20


def allowed(plan: set[str]) -> bool:
    """Fix every repair in or out and ask whether the model accepts the plan."""
    model, x = build(REPAIRS, BUDGET, FLOOR)
    for rid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if rid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_plan_over_budget_is_refused():
    assert allowed({"L1", "L4"}) is True
    assert allowed({"L1", "L2", "L3"}) is False


def test_a_plan_below_the_risk_floor_is_refused():
    assert allowed({"L1", "L4"}) is True
    assert allowed({"L2", "L5"}) is False


def test_at_most_one_repair_per_main():
    assert allowed({"L3"}) is True
    assert allowed({"L3", "L4"}) is False


def test_repairs_on_no_main_are_independent():
    assert allowed({"L1", "L2"}) is True
    assert allowed({"L1", "L2", "L3", "L4"}) is False


def test_the_best_plan_has_the_most_npv_above_the_floor():
    model, x = build(REPAIRS, BUDGET, FLOOR)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert {rid for rid, v in x.items() if result.variable_values(v) > 0.5} == {"L1", "L2", "L5"}
    assert result.objective_value() == 75
