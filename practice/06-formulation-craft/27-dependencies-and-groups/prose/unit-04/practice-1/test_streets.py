from ortools.math_opt.python import mathopt

from streets import Project, build

# A city's streets, not the lesson's portfolio.
YEARS = tuple(range(2027, 2034))
PROJECTS = [
    Project("MAIN-ELM", (2027, 2028, 2029), 2),
    Project("MAIN-OAK", (2028, 2029), 3),
    Project("PAVE-ELM", YEARS),
    Project("PAVE-OAK", YEARS),
    Project("PAVE-ASH", YEARS),
]
AFTER = {"PAVE-ELM": ("MAIN-ELM", 1), "PAVE-OAK": ("MAIN-OAK", 0)}


def allowed(plan: set[tuple[str, int]]) -> bool:
    """Fix every start variable to the plan and ask whether the model accepts it."""
    model, x = build(PROJECTS, AFTER)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_resurfacing_waits_for_its_main():
    assert allowed({("MAIN-ELM", 2027), ("PAVE-ELM", 2032)}) is True
    assert allowed({("PAVE-ELM", 2032)}) is False


def test_a_street_without_a_main_is_free():
    assert allowed({("PAVE-ASH", 2027), ("MAIN-OAK", 2028)}) is True
    assert allowed({("PAVE-ASH", 2027), ("PAVE-OAK", 2027)}) is False


def test_resurfacing_waits_for_the_main_to_finish():
    assert allowed({("MAIN-OAK", 2028), ("PAVE-OAK", 2031)}) is True
    assert allowed({("MAIN-OAK", 2028), ("PAVE-OAK", 2029)}) is False


def test_the_settling_year_counts():
    assert allowed({("MAIN-ELM", 2028), ("PAVE-ELM", 2030)}) is False


def test_resurfacing_right_after_settling_is_allowed():
    assert allowed({("MAIN-ELM", 2028), ("PAVE-ELM", 2031)}) is True
    assert allowed({("MAIN-ELM", 2029), ("PAVE-ELM", 2031)}) is False
