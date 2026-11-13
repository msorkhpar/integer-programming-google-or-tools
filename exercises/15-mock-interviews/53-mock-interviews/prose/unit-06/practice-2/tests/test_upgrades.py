from ortools.math_opt.python import mathopt

from upgrades import Limits, Project, build

# A telecom operator's tower upgrades, not the lessons' portfolio.
PROJECTS = [
    Project("A", 40, 3, "N", 10),
    Project("B", 30, 2, "N", 8),
    Project("C", 30, 4, "S", 9),
    Project("D", 20, 1, "S", 4),
    Project("E", 50, 2, "W", 12),
]
LIMITS = Limits(budget=100, crew=7, region_cap={"N": 1, "S": 2, "W": 1},
                conflicts=[("C", "E")], needs=[("D", "C")])


def allowed(plan: set[str], projects: list[Project] = PROJECTS) -> bool:
    """Fix every project in or out and ask HiGHS whether the model accepts the plan."""
    model, x = build(projects, LIMITS)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_plan_over_budget_is_refused():
    assert allowed({"A"}) is True
    assert allowed({"A", "C", "E"}) is False


def test_a_plan_over_the_crew_weeks_is_refused():
    assert allowed({"A"}) is True
    assert allowed({"A", "C", "D"}) is False


def test_a_region_over_its_cap_is_refused():
    assert allowed({"A"}) is True
    assert allowed({"A", "B"}) is False


def test_a_conflicting_pair_is_refused():
    assert allowed({"E"}) is True
    assert allowed({"C", "E"}) is False


def test_a_need_runs_one_way():
    assert allowed({"C"}) is True
    assert allowed({"D"}) is False


def test_each_region_has_its_own_cap():
    assert allowed({"A", "C"}) is True
    assert allowed({"A", "B"}) is False


def test_a_region_with_no_cap_entry_has_no_cap():
    towers = PROJECTS + [Project("G", 5, 0, "X", 1), Project("H", 5, 0, "X", 1), Project("I", 5, 0, "X", 1)]
    assert allowed({"G", "H", "I"}, towers) is True
    assert allowed({"A", "B", "G"}, towers) is False
