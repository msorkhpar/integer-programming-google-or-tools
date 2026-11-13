from strong import strong_choice


def test_the_candidate_with_the_largest_product_of_drops_wins():
    assert strong_choice(100.0, {"a": (96.0, 97.0), "b": (94.0, 95.0)}) == "b"


def test_ties_go_to_the_first_candidate_listed():
    assert strong_choice(100.0, {"a": (98.0, 97.0), "b": (97.0, 98.0)}) == "a"
    assert strong_choice(100.0, {"b": (97.0, 98.0), "a": (98.0, 97.0)}) == "b"


def test_the_product_prefers_a_balanced_split_to_a_lopsided_one():
    assert strong_choice(100.0, {"a": (70.0, 99.9), "b": (94.0, 95.0)}) == "b"


def test_a_zero_drop_is_lifted_to_epsilon():
    assert strong_choice(100.0, {"b": (100.0, 97.0), "a": (100.0, 50.0)}) == "a"


def test_an_infeasible_child_is_the_largest_drop():
    assert strong_choice(100.0, {"a": (60.0, 55.0), "b": (None, 99.0)}) == "b"
