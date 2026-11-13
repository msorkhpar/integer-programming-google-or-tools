from claim import faster


def test_a_margin_on_every_repetition_allows_the_claim():
    assert faster([1.0, 1.2, 0.9], [4.1, 3.9, 4.4], 2.0) == "a"
    assert faster([1.0, 1.2, 0.9], [1.1, 1.0, 1.4], 2.0) == "neither"


def test_the_other_solver_can_be_the_faster_one():
    assert faster([5.0, 6.5, 5.5], [2.0, 2.1, 1.9], 2.0) == "b"


def test_one_repetition_short_of_the_factor_blocks_the_claim():
    # Ratios 6.0, 5.0 and 1.5: the mean is above 2, one repetition is not.
    assert faster([1.0, 1.0, 2.0], [6.0, 5.0, 3.0], 2.0) == "neither"


def test_a_ratio_exactly_at_the_factor_allows_the_claim():
    assert faster([1.0, 2.0], [3.0, 6.0], 3.0) == "a"
    assert faster([3.0, 6.0], [1.0, 2.0], 3.0) == "b"
