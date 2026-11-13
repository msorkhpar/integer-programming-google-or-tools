from ortools.math_opt.python import mathopt

from water_rules import Project, build

# A water utility's candidate projects, not the lesson's portfolio.
PROJECTS = [Project(pid, 100) for pid in ("TX", "NM", "SM", "R", "PS", "NI", "T", "OI", "MP", "BU")]
NEEDS_ANY = {"TX": ["NM", "SM"]}                   # treatment expansion needs a main to carry its output
ALL_TRIGGER = [(["R", "PS", "NI"], "T")]           # reservoir, pump station and new intake need telemetry
NEVER_WITH = [("OI", "NI")]                        # rehabilitate the old intake or build a new one
TOGETHER = [("MP", "BU")]                          # meters and billing go live together


def allowed(plan: set[str]) -> bool:
    """Fix every project's variable to the plan and ask whether the model accepts it."""
    model, x = build(PROJECTS, 10_000, NEEDS_ANY, ALL_TRIGGER, NEVER_WITH, TOGETHER)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_project_needs_one_of_its_supports():
    assert allowed({"TX", "NM"}) is True
    assert allowed({"TX"}) is False


def test_two_projects_that_cannot_coexist_are_never_both_funded():
    assert allowed({"OI"}) is True
    assert allowed({"OI", "NI"}) is False


def test_a_full_group_triggers_its_consequence():
    assert allowed({"R", "PS", "NI", "T"}) is True
    assert allowed({"R", "PS", "NI"}) is False


def test_paired_projects_are_funded_together():
    assert allowed({"MP", "BU"}) is True
    assert allowed({"MP"}) is False


def test_part_of_a_group_does_not_trigger_the_consequence():
    assert allowed({"R", "PS"}) is True
    assert allowed({"R", "PS", "NI"}) is False


def test_a_project_may_have_several_supports_funded():
    assert allowed({"TX", "NM", "SM"}) is True
    assert allowed({"TX"}) is False


def test_the_second_member_of_a_pair_cannot_go_alone():
    assert allowed(set()) is True
    assert allowed({"BU"}) is False
