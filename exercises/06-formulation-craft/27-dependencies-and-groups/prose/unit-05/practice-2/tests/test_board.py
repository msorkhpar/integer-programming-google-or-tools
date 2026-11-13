from ortools.math_opt.python import mathopt

from board import Project, build

# A water board's candidates, not the lesson's portfolio.
PROJECTS = [
    Project("M1", "maintenance", 200), Project("M2", "maintenance", 150), Project("M3", "maintenance", 300),
    Project("M4", "maintenance", 120), Project("G1", "growth", 400), Project("G2", "growth", 250),
    Project("G3", "growth", 100),
]
BUDGET, USE, LOW, HIGH = 1000, 0.75, 0.3, 0.5


def allowed(plan: set[str]) -> bool:
    """Fix every variable to the plan and ask whether the model accepts it."""
    model, x = build(PROJECTS, BUDGET, USE, LOW, HIGH)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


GOOD = {"M1", "M2", "G1", "G3"}          # 850 spent, 350 of it maintenance


def test_the_plan_uses_its_budget():
    assert allowed(GOOD) is True
    assert allowed({"M1", "G1"}) is False
    assert allowed(GOOD | {"G2"}) is False


def test_maintenance_stays_in_its_band():
    assert allowed({"M2", "G1", "G2", "G3"}) is False
    assert allowed({"M1", "M2", "M3", "G2"}) is False


def test_a_small_plan_needs_only_its_own_share():
    assert allowed({"M2", "M4", "G1", "G3"}) is True
    assert allowed({"M2", "M4", "G1"}) is False


def test_a_large_maintenance_sum_can_still_be_too_much():
    assert allowed({"M1", "M3", "G1", "G3"}) is True
    assert allowed({"M1", "M2", "M4", "G1"}) is False
