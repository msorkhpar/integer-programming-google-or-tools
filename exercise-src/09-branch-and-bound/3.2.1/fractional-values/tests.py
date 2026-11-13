from fractional import fractional


def test_halves_and_quarters_are_fractional_and_zeros_and_ones_are_not():
    assert fractional({"a": 0.0, "b": 0.5, "c": 1.0, "d": 0.25}) == ["b", "d"]


def test_names_come_back_in_the_order_of_the_solution():
    assert fractional({"z": 0.7, "m": 1.0, "a": 0.3}) == ["z", "a"]


def test_float_noise_near_a_whole_number_is_not_fractional():
    x = {"a": 0.9999999, "b": 0.5, "c": 2e-9, "d": 1.0000004}
    assert fractional(x) == ["b"]
    assert fractional({"a": 0.9999, "b": 0.5}) == ["a", "b"]


def test_a_general_integer_is_judged_against_its_nearest_whole_number():
    x = {"trucks_a": 3.0, "trucks_b": 2.5, "shift": -1.5, "trucks_c": 4.0000001, "delta": -2.0}
    assert fractional(x) == ["trucks_b", "shift"]
