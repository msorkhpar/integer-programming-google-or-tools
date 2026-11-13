from ortools.math_opt.python import mathopt

from roofs import build

# A campus's roofs, not the lesson's portfolio.
YEARS = tuple(range(2027, 2037))
ROOFS = {"LIB": (YEARS, YEARS), "GYM": ((2027, 2028, 2029), (2030, 2031, 2032))}
GAP, WARRANTY = 3, 2


def allowed(patches: set[tuple[str, int]], replacements: set[tuple[str, int]]) -> bool:
    """Fix every variable to the plan and ask whether the model accepts it."""
    model, patch, replace = build(ROOFS, GAP, WARRANTY)
    for chosen, variables in ((patches, patch), (replacements, replace)):
        for key, var in variables.items():
            var.lower_bound = var.upper_bound = 1.0 if key in chosen else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_patch_then_a_late_replacement_is_allowed():
    assert allowed({("LIB", 2027)}, {("LIB", 2031)}) is True
    assert allowed({("LIB", 2028)}, {("LIB", 2030)}) is False
    assert allowed({("GYM", 2029)}, {("GYM", 2030)}) is False


def test_a_patch_or_a_replacement_alone_is_allowed():
    assert allowed({("LIB", 2030)}, {("GYM", 2032)}) is True
    assert allowed({("GYM", 2028)}, {("LIB", 2027)}) is True
    assert allowed({("LIB", 2029)}, {("LIB", 2030)}) is False


def test_no_patch_under_the_new_roofs_warranty():
    assert allowed({("LIB", 2030)}, {("LIB", 2030)}) is False
    assert allowed({("LIB", 2032)}, {("LIB", 2030)}) is False


def test_a_patch_after_the_warranty_is_allowed():
    assert allowed({("LIB", 2033)}, {("LIB", 2030)}) is True
    assert allowed({("LIB", 2031)}, {("LIB", 2030)}) is False


def test_a_replacement_exactly_the_gap_after_a_patch_is_allowed():
    assert allowed({("LIB", 2027)}, {("LIB", 2030)}) is True
    assert allowed({("LIB", 2028)}, {("LIB", 2030)}) is False
