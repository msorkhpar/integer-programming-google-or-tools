import itertools
from fractions import Fraction

from scaling import scale_row


def holds(coefficients, rhs, sense, xs) -> bool:
    lhs = sum(Fraction(c) * x for c, x in zip(coefficients, xs))
    return {"<=": lhs <= Fraction(rhs), ">=": lhs >= Fraction(rhs), "==": lhs == Fraction(rhs)}[sense]


def same_points(coefficients, rhs, sense, values=(0, 1, 2)) -> bool:
    """The scaled row is whole and allows exactly the integer points (each x in `values`) the original allows."""
    whole, bound = scale_row(coefficients, rhs, sense)
    if not all(isinstance(c, int) for c in whole) or bound is None or not isinstance(bound, int):
        return False
    return all(holds(coefficients, rhs, sense, xs) == holds([str(c) for c in whole], str(bound), sense, xs)
               for xs in itertools.product(values, repeat=len(coefficients)))


def test_a_less_than_row_keeps_its_points():
    # A lab's bench hours: 0.5, 1.25 and 2.4 hours per sample run, 6.3 hours free.
    assert same_points(["0.5", "1.25", "2.4"], "6.3", "<=") is True


def test_a_greater_than_row_keeps_its_points():
    # A diet's protein floor: 1.5, 0.8 and 2.25 grams per portion, at least 4.1 grams.
    assert same_points(["1.5", "0.8", "2.25"], "4.1", ">=") is True


def test_an_equality_with_a_reachable_total_keeps_its_points():
    # 0.5 and 0.25 litre bottles that must add up to 1.75 litres.
    assert same_points(["0.5", "0.25"], "1.75", "==", values=range(8)) is True


def test_the_multiplier_is_the_smallest_that_works():
    assert scale_row(["1.5", "0.75", "2"], "5", "<=") == ([6, 3, 8], 20)


def test_an_equality_no_whole_point_can_meet_says_so():
    # 0.5 x + 1.5 y = 1.25 has no integer solution: times 2 it is x + 3y = 2.5.
    assert scale_row(["0.5", "1.5"], "1.25", "==") == ([1, 3], None)
