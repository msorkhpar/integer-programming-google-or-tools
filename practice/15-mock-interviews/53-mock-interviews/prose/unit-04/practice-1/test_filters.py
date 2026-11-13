from filters import deletion_filter


def oracle(*conflicts):
    """A stand-in for a solver: a set of rules is infeasible when it contains a whole conflict."""
    def feasible(subset):
        return not any(set(c) <= set(subset) for c in conflicts)
    return feasible


def test_the_result_is_a_conflict_with_nothing_to_spare():
    feasible = oracle({"a", "b"}, {"c", "d", "e"})
    assert deletion_filter(["a", "b", "c", "d", "e"], feasible) == ["c", "d", "e"]


def test_every_rule_left_is_needed():
    feasible = oracle({"p", "q"}, {"q", "r", "s"})
    result = deletion_filter(["p", "q", "r", "s"], feasible)
    assert result == ["q", "r", "s"]
    assert not feasible(result)
    assert all(feasible([r for r in result if r != name]) for name in result)


def test_the_conflict_tested_last_survives():
    feasible = oracle({"a", "b"}, {"c", "d", "e"})
    assert deletion_filter(["e", "d", "c", "b", "a"], feasible) == ["b", "a"]


def test_rules_that_can_all_hold_have_no_conflict():
    feasible = oracle({"x", "y"})
    assert deletion_filter(["x", "z", "w"], feasible) == []
