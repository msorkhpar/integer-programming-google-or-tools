"""The checker's own rules (the spec-checks capability), each on a small spec written in the test."""

from pathlib import Path

from specs_check import Issue, check_spec, passes, validate

ROOT = Path(__file__).resolve().parents[1]
FITS = "#### Scenario: Fits\n- **WHEN** a plan spends $900k\n- **THEN** the plan is allowed\n"


def spec(block):
    return ("# demo Specification\n\n## Purpose\nA spec written for one test of the checker, and for nothing else."
            "\n\n## Requirements\n\n" + block)


def test_a_requirement_with_no_text_is_an_error():
    issues = check_spec(spec("### Requirement: Budget\n\n" + FITS), "demo")
    assert issues == [Issue("ERROR", "demo", 'requirement "Budget" has no text under its header')]


def test_text_without_shall_or_must_is_a_warning():
    issues = check_spec(spec("### Requirement: Budget\nThe planner keeps the budget.\n\n" + FITS), "demo")
    assert issues == [Issue("WARNING", "demo", 'requirement "Budget" should contain SHALL or MUST in its text')]


def test_a_keyword_only_in_the_header_does_not_count():
    name = "The planner SHALL keep the budget"
    issues = check_spec(spec(f"### Requirement: {name}\nSpending stays within it.\n\n" + FITS), "demo")
    assert issues == [Issue("WARNING", "demo", f'requirement "{name}" should contain SHALL or MUST in its text')]


def test_a_requirement_without_scenarios_is_an_error():
    issues = check_spec(spec("### Requirement: Budget\nThe planner SHALL keep the budget.\n"), "demo")
    assert issues == [Issue("ERROR", "demo", 'requirement "Budget" must include at least one scenario')]


def test_an_empty_scenario_does_not_count():
    issues = check_spec(spec("### Requirement: Budget\nThe planner SHALL keep the budget.\n\n#### Scenario: Fits\n"),
                        "demo")
    assert issues == [Issue("ERROR", "demo", 'requirement "Budget" must include at least one scenario')]


def test_a_scenario_without_then_is_a_warning():
    steps = "#### Scenario: Fits\n- **WHEN** a plan spends $900k\n- the plan is allowed\n"
    issues = check_spec(spec("### Requirement: Budget\nThe planner SHALL keep the budget.\n\n" + steps), "demo")
    assert issues == [Issue("WARNING", "demo", 'scenario "Fits" is missing a THEN step')]


def test_strict_mode_fails_on_a_warning():
    issues = check_spec(spec("### Requirement: Budget\nThe planner keeps the budget.\n\n" + FITS), "demo")
    assert passes(issues, strict=False)
    assert not passes(issues, strict=True)


def test_these_specs_pass_strict_validation():
    found = validate(ROOT)
    assert found
    assert all(passes(issues, strict=True) for issues in found.values()), found
