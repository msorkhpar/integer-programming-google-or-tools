from ortools.math_opt.python import mathopt

from selection import Project, build_model, solve

YARD = [
    Project("K1", 20, 40, must_do=True),
    Project("K2", 25, 35),
    Project("K3", 15, 40, parent="K2"),
    Project("K4", 20, 30, group="bay"),
    Project("K5", 15, 28, group="bay"),
    Project("K6", 30, 25),
]
BUDGET = 100


def allows(plan: set[str]) -> bool:
    """Does the model accept exactly this plan? Fix every variable and ask the solver."""
    model, x = build_model(YARD, BUDGET)
    for pid, var in x.items():
        value = 1.0 if pid in plan else 0.0
        var.lower_bound = var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_the_solver_returns_the_best_allowed_plan():
    value, plan = solve(YARD, BUDGET)
    assert round(value) == 145 and plan == frozenset({"K1", "K2", "K3", "K4"})


def test_a_must_do_project_is_always_funded():
    assert not allows({"K2", "K3", "K4", "K6"})
    assert allows({"K1", "K6"})


def test_a_child_needs_its_parent_but_not_the_reverse():
    assert not allows({"K1", "K3"})
    assert allows({"K1", "K2"})


def test_at_most_one_alternative_is_funded():
    assert allows({"K1", "K6"})
    assert not allows({"K1", "K4", "K5"})
