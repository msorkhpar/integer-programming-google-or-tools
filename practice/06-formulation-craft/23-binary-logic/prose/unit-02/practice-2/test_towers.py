from ortools.math_opt.python import mathopt

from towers import Upgrade, build

# A rural carrier's upgrades, not the lesson's portfolio.
UPGRADES = [Upgrade("T1", 100), Upgrade("B1", 60), Upgrade("T2", 80), Upgrade("C1", 50),
            Upgrade("C2", 40), Upgrade("N1", 35)]
PERMITS = {"river": (25, ["C1", "C2"])}
BUNDLES = [("T1", "B1", 40)]


def allowed(plan: set[str], budget: int) -> bool:
    """Fix which upgrades are built and ask whether the model accepts the plan."""
    model, x = build(UPGRADES, PERMITS, BUNDLES, budget)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_permit_fee_is_charged_when_a_project_needs_it():
    # C1: 50 + 25 = 75. C1 + N1: 85 + 25 = 110.
    assert allowed({"C1"}, budget=100) is True
    assert allowed({"C1", "N1"}, budget=100) is False


def test_a_bundle_discount_is_applied_when_both_members_are_funded():
    # T1 + B1: 160 - 40 = 120. T1 + B1 + N1: 195 - 40 = 155.
    assert allowed({"T1", "B1"}, budget=150) is True
    assert allowed({"T1", "B1", "N1"}, budget=150) is False


def test_a_permit_is_paid_once_however_many_projects_use_it():
    # C1 + C2: 90 + 25 = 115. C1 + C2 + N1: 125 + 25 = 150.
    assert allowed({"C1", "C2"}, budget=120) is True
    assert allowed({"C1", "C2", "N1"}, budget=120) is False


def test_a_plan_needing_no_permit_pays_no_fee():
    # N1: 35. C1: 50 + 25 = 75.
    assert allowed({"N1"}, budget=40) is True
    assert allowed({"C1"}, budget=40) is False


def test_one_member_of_a_bundle_gets_no_discount():
    # T1 + B1: 160 - 40 = 120. T1 + N1: 135, with no discount.
    assert allowed({"T1", "B1"}, budget=130) is True
    assert allowed({"T1", "N1"}, budget=130) is False
