from classify import classify


def test_an_infeasible_node_is_pruned_as_infeasible():
    assert classify("infeasible", 0.0, False, 50.0) == "infeasible"
    assert classify("infeasible", 0.0, False, None) == "infeasible"


def test_a_fractional_node_above_the_incumbent_is_branched():
    assert classify("optimal", 72.5, False, 60.0) == "branch"


def test_an_integral_node_above_the_incumbent_becomes_the_incumbent():
    assert classify("optimal", 66.0, True, 60.0) == "incumbent"


def test_with_no_incumbent_yet_nothing_is_pruned_by_bound():
    assert classify("optimal", 10.5, False, None) == "branch"
    assert classify("optimal", 3.0, True, None) == "incumbent"


def test_a_bound_equal_to_the_incumbent_is_pruned():
    assert classify("optimal", 60.0, False, 60.0) == "bound"
    assert classify("optimal", 60.5, False, 60.0) == "branch"


def test_a_worse_integral_node_is_pruned_by_bound():
    assert classify("optimal", 55.0, True, 60.0) == "bound"
    assert classify("optimal", 61.0, True, 60.0) == "incumbent"


def test_whole_values_round_the_bound_down():
    assert classify("optimal", 100.6, False, 100.0, whole_values=True) == "bound"
    assert classify("optimal", 100.6, False, 100.0) == "branch"
    assert classify("optimal", 101.2, False, 100.0, whole_values=True) == "branch"


def test_rounding_down_forgives_lp_noise_just_below_a_whole_number():
    assert classify("optimal", 101.9999999999, False, 101.0, whole_values=True) == "branch"
    assert classify("optimal", 101.9999, False, 101.0, whole_values=True) == "bound"
