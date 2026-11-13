from pick import pick


def ev(solved=12, runs=12, repeat=True, spread=1.0):
    return {"solved": solved, "runs": runs, "repeat": repeat, "spread": spread}


def test_the_steadier_finalist_is_the_default_and_the_other_the_fallback():
    evidence = {"Rowan": ev(spread=1.8), "Hazel": ev(spread=1.2)}
    assert pick(["Rowan", "Hazel"], evidence) == ("Hazel", "Rowan")


def test_a_solver_that_failed_a_run_is_not_a_finalist():
    evidence = {"Rowan": ev(spread=1.8), "Hazel": ev(spread=1.2), "Larch": ev(solved=11, spread=1.0)}
    assert pick(["Rowan", "Hazel", "Larch"], evidence) == ("Hazel", "Rowan")


def test_a_solver_whose_runs_did_not_repeat_is_not_a_finalist():
    evidence = {"Rowan": ev(spread=1.8), "Hazel": ev(repeat=False, spread=1.2)}
    assert pick(["Rowan", "Hazel"], evidence) == ("Rowan", None)


def test_only_solvers_that_passed_the_requirements_are_considered():
    evidence = {"Rowan": ev(spread=1.8), "Hazel": ev(spread=1.2), "Yew": ev(spread=1.0)}
    assert pick(["Rowan", "Hazel"], evidence) == ("Hazel", "Rowan")


def test_a_tie_on_spread_goes_to_the_alphabetically_first():
    evidence = {"Rowan": ev(spread=1.5), "Hazel": ev(spread=1.5)}
    assert pick(["Rowan", "Hazel"], evidence) == ("Hazel", "Rowan")


def test_a_passing_solver_with_no_evidence_is_not_a_finalist():
    evidence = {"Rowan": ev(spread=1.8)}
    try:
        picked = pick(["Rowan", "Hazel"], evidence)
    except KeyError as error:       # a lookup of the unmeasured solver is a wrong answer here
        raise AssertionError(f"pick looked up a solver with no evidence: {error}") from None
    assert picked == ("Rowan", None)
