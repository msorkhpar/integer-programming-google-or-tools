from claims import judge_claim


def test_a_maximization_sorts_claims_below_inside_and_above_the_bracket():
    assert judge_claim(4_000, incumbent=5_100, bound=5_300, maximize=True) == "found"
    assert judge_claim(5_200, incumbent=5_100, bound=5_300, maximize=True) == "possible"
    assert judge_claim(5_301, incumbent=5_100, bound=5_300, maximize=True) == "impossible"


def test_a_minimization_reads_the_bracket_the_other_way():
    assert judge_claim(3_400, incumbent=3_200, bound=2_900, maximize=False) == "found"
    assert judge_claim(3_000, incumbent=3_200, bound=2_900, maximize=False) == "possible"
    assert judge_claim(2_800, incumbent=3_200, bound=2_900, maximize=False) == "impossible"


def test_a_claim_equal_to_the_bound_is_still_possible():
    assert judge_claim(5_300, incumbent=5_100, bound=5_300, maximize=True) == "possible"
    assert judge_claim(2_900, incumbent=3_200, bound=2_900, maximize=False) == "possible"


def test_a_claim_equal_to_the_incumbent_is_found():
    assert judge_claim(5_100, incumbent=5_100, bound=5_300, maximize=True) == "found"
    assert judge_claim(3_200, incumbent=3_200, bound=2_900, maximize=False) == "found"


def test_with_no_incumbent_a_claim_within_the_bound_is_only_possible():
    assert judge_claim(10, incumbent=None, bound=5_300, maximize=True) == "possible"
    assert judge_claim(6_000, incumbent=None, bound=5_300, maximize=True) == "impossible"
    assert judge_claim(9_000, incumbent=None, bound=2_900, maximize=False) == "possible"
