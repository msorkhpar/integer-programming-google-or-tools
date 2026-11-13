from pareto import unbeaten

UP = ("max", "max")


def test_options_beaten_on_both_measures_are_dropped():
    options = {"A": (8, 2), "B": (5, 5), "C": (2, 9), "D": (4, 4), "E": (1, 8)}
    assert unbeaten(options, UP) == {"A", "B", "C"}


def test_identical_options_are_both_kept():
    options = {"A": (8, 2), "B": (5, 5), "B2": (5, 5), "C": (2, 9)}
    assert unbeaten(options, UP) == {"A", "B", "B2", "C"}


def test_an_option_that_only_ties_on_one_measure_is_dropped():
    options = {"A": (8, 2), "B": (5, 5), "F": (5, 3), "C": (2, 9)}
    assert unbeaten(options, UP) == {"A", "B", "C"}


def test_a_measure_to_minimize_counts_lower_as_better():
    # (cost, riders): cost is minimized
    options = {"cheap": (10, 50), "mid": (20, 80), "dear": (30, 70), "dearest": (40, 90)}
    assert unbeaten(options, ("min", "max")) == {"cheap", "mid", "dearest"}
