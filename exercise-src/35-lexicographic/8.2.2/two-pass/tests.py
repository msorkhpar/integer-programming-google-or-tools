import itertools

import pytest
from ortools.math_opt.python import mathopt

from two_pass import two_pass

COST = [5, 4, 3, 3, 2, 2]          # $100k per main
LEAKS = [12, 10, 8, 7, 4, 3]       # leaks avoided per year
HOURS = [7, 9, 3, 8, 2, 1]         # customer disruption hours
BUDGET = 10


def network(leaks=LEAKS):
    model = mathopt.Model(name="mains")
    x = [model.add_binary_variable(name=f"main_{i}") for i in range(len(COST))]
    model.add_linear_constraint(sum(c * v for c, v in zip(COST, x)) <= BUDGET, name="budget")
    first = mathopt.LinearExpression() + sum(a * v for a, v in zip(leaks, x))
    second = mathopt.LinearExpression() + sum(h * v for h, v in zip(HOURS, x))
    return model, first, second


def native(f, g, f_max, g_max, abs_tol=0.0, rel_tol=0.0, least=0):
    """The answer of a hierarchical solve, by enumerating every plan: (f, g) of the chosen plan.

    `least` is the fewest mains a plan must renew."""
    plans = [p for p in itertools.product((0, 1), repeat=len(COST))
             if sum(c * b for c, b in zip(COST, p)) <= BUDGET and sum(p) >= least]
    fv = {p: sum(a * b for a, b in zip(f, p)) for p in plans}
    gv = {p: sum(a * b for a, b in zip(g, p)) for p in plans}
    best = max(fv.values()) if f_max else min(fv.values())
    loss = max(abs_tol, rel_tol * abs(best))
    kept = [p for p in plans if (fv[p] >= best - loss if f_max else fv[p] <= best + loss)]
    pick = max(kept, key=gv.get) if g_max else min(kept, key=gv.get)
    return fv[pick], gv[pick]


def test_with_no_tolerance_it_matches_the_native_answer():
    model, leaks, hours = network()
    got = two_pass(model, leaks, hours, first_max=True, second_max=False)
    assert got == pytest.approx(native(LEAKS, HOURS, True, False))


def test_a_relative_tolerance_lets_the_second_objective_improve():
    model, leaks, hours = network()
    got = two_pass(model, leaks, hours, first_max=True, second_max=False, rel_tol=0.1)
    want = native(LEAKS, HOURS, True, False, rel_tol=0.1)
    assert got == pytest.approx(want)
    assert want[1] < native(LEAKS, HOURS, True, False)[1]          # the tolerance bought something


def test_a_minimized_first_objective_may_rise_by_its_tolerance():
    model, leaks, hours = network()
    # Minimizing hours alone funds nothing; require at least 15 leaks avoided first.
    model.add_linear_constraint(leaks >= 15, name="leak_target")
    got = two_pass(model, hours, leaks, first_max=False, second_max=True, abs_tol=3.0)
    assert got == pytest.approx((9.0, 16.0))


def test_the_model_is_given_back_without_the_kept_row():
    model, leaks, hours = network()
    two_pass(model, leaks, hours, first_max=True, second_max=False, abs_tol=0.0)
    two_pass(model, leaks, hours, first_max=True, second_max=False, rel_tol=0.1)
    got = two_pass(model, hours, leaks, first_max=False, second_max=True, abs_tol=5.0)
    assert got == pytest.approx(native(HOURS, LEAKS, False, True, abs_tol=5.0))
    assert len(list(model.linear_constraints())) == 1


def test_a_relative_tolerance_uses_the_size_of_a_negative_best():
    # Net leaks avoided after new breaks from the works: every value is negative, and the regulator
    # requires at least two mains renewed, so the best net value is below zero.
    net = [a - 20 for a in LEAKS]
    model, first, hours = network(net)
    model.add_linear_constraint(sum(model.variables()) >= 2, name="at_least_two")
    got = two_pass(model, first, hours, first_max=True, second_max=False, rel_tol=0.5)
    assert got == pytest.approx(native(net, HOURS, True, False, rel_tol=0.5, least=2))
