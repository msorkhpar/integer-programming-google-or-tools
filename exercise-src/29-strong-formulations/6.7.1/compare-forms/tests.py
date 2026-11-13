from ortools.math_opt.python import mathopt

from compare import compare

# Two yes/no decisions u and v, and formulations of small rules about them; not the lesson's model.


def formulation(rows, sense="max"):
    """A builder: the LP relaxation with these rows (functions of u and v) and a given objective."""
    def build(objective):
        model = mathopt.Model()
        u = model.add_variable(lb=0, ub=1, name="u")
        v = model.add_variable(lb=0, ub=1, name="v")
        for row in rows:
            model.add_linear_constraint(row(u, v))
        expr = objective[0] * u + objective[1] * v
        model.maximize(expr) if sense == "max" else model.minimize(expr)
        return model
    return build


# "At most one of u, v": u + v <= 1 is the hull; 2u + 2v <= 3 allows the same 0/1 points.
AT_MOST_ONE = formulation([lambda u, v: u + v <= 1])
LOOSE_AT_MOST_ONE = formulation([lambda u, v: 2 * u + 2 * v <= 3])


def test_the_stronger_of_two_maximizing_forms_is_named():
    objectives = [(1, 1), (1, 2), (3, 1)]
    assert compare(AT_MOST_ONE, LOOSE_AT_MOST_ONE, objectives) == "a"
    assert compare(LOOSE_AT_MOST_ONE, AT_MOST_ONE, objectives) == "b"


def test_when_minimizing_the_higher_floor_is_tighter():
    # "At least one of u, v", minimizing: u + v >= 1 against 2u + 2v >= 1.
    strong = formulation([lambda u, v: u + v >= 1], sense="min")
    weak = formulation([lambda u, v: 2 * u + 2 * v >= 1], sense="min")
    assert compare(strong, weak, [(1, 1), (2, 3)], sense="min") == "a"


def test_forms_that_each_win_one_objective_are_neither():
    # Both allow exactly the 0/1 points of "at most one"; their regions do not contain each other.
    left = formulation([lambda u, v: u + 2 * v <= 2])
    right = formulation([lambda u, v: 2 * u + v <= 2])
    assert compare(left, right, [(1, 2), (2, 1)]) == "neither"


def test_forms_with_equal_bounds_everywhere_are_the_same():
    doubled = formulation([lambda u, v: 2 * u + 2 * v <= 2])
    assert compare(AT_MOST_ONE, doubled, [(1, 1), (1, 3), (2, 1)]) == "same"
