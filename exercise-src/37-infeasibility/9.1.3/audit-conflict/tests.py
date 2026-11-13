from audit import audit


def oracle(*clashes):
    sets = [set(c) for c in clashes]
    return lambda on: any(c <= set(on) for c in sets)


def test_a_true_iis_passes_and_an_extra_member_is_named():
    clash = oracle(["possession_wk12", "grind_wk12", "night_only"])
    assert audit(["possession_wk12", "grind_wk12", "night_only"], clash) == {"infeasible": True, "not_needed": []}
    assert audit(["possession_wk12", "grind_wk12", "night_only", "crew_max_3"], clash) == {
        "infeasible": True, "not_needed": ["crew_max_3"]}


def test_a_claim_that_is_not_infeasible_is_reported_as_such():
    clash = oracle(["possession_wk12", "grind_wk12", "night_only"])
    assert audit(["grind_wk12", "night_only"], clash) == {"infeasible": False, "not_needed": []}


def test_each_member_is_tested_against_the_whole_claim():
    # Two conflicts share a member: either other member alone could go, though not both.
    clash = oracle(["possession_wk12", "grind_wk12"], ["possession_wk12", "night_only"])
    assert audit(["possession_wk12", "grind_wk12", "night_only"], clash) == {
        "infeasible": True, "not_needed": ["grind_wk12", "night_only"]}
