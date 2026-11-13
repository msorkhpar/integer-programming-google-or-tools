from most_fractional import most_fractional


def test_the_value_closest_to_one_half_is_chosen():
    assert most_fractional({"a": 0.9, "b": 0.45, "c": 0.2}) == "b"


def test_an_all_integral_solution_gives_none():
    assert most_fractional({"a": 0.0, "b": 1.0, "c": 1.0}) is None


def test_ties_go_to_the_first_variable_listed():
    assert most_fractional({"a": 1.0, "b": 0.25, "c": 0.75}) == "b"
    assert most_fractional({"a": 1.0, "c": 0.75, "b": 0.25}) == "c"


def test_a_general_integer_is_measured_by_its_fractional_part():
    assert most_fractional({"open": 0.4, "crews": 3.5, "vans": 2.0}) == "crews"


def test_float_noise_is_not_a_candidate():
    assert most_fractional({"a": 0.9999999, "b": 1.0}) is None
    assert most_fractional({"a": 2e-9, "b": 0.99}) == "b"
