import numpy as np

from leq import to_leq

# A depot stocks three spare parts; x[j] is how many of part j to order.


def test_less_or_equal_rules_go_in_as_written():
    rules = [({0: 2, 1: 1, 2: 3}, "<=", 40),      # shelf space
             ({1: 1, 2: -1}, "<=", 0)]           # no more of part 1 than of part 2
    A, b = to_leq(rules, 3)
    assert np.array_equal(A, [[2, 1, 3], [0, 1, -1]])
    assert np.array_equal(b, [40, 0])


def test_greater_or_equal_rule_is_flipped_whole():
    rules = [({0: 1, 1: 1}, ">=", 5)]            # at least 5 of parts 0 and 1 together
    A, b = to_leq(rules, 3)
    assert np.array_equal(A, [[-1, -1, 0]])
    assert np.array_equal(b, [-5])


def test_equality_rule_becomes_two_rows():
    rules = [({0: 50, 1: 20, 2: 10}, "<=", 900),
             ({2: 1}, "==", 4)]                  # exactly 4 of part 2
    A, b = to_leq(rules, 3)
    assert np.array_equal(A, [[50, 20, 10], [0, 0, 1], [0, 0, -1]])
    assert np.array_equal(b, [900, 4, -4])


def test_a_variable_no_rule_mentions_still_has_a_column():
    rules = [({0: 1, 1: 2}, "<=", 6)]            # part 2 and part 3 appear in no rule
    A, b = to_leq(rules, 4)
    assert np.array_equal(A, [[1, 2, 0, 0]])
    assert np.array_equal(b, [6])
