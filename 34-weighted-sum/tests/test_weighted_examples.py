"""The module 34 examples: weighted sums on GridCap small, and a plan no weighting reaches."""

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from two_objectives import build, plan_of, score, solve_highs, weighted


@pytest.fixture(scope="module")
def sm():
    return build(generate("small"))


def test_the_ends_are_lesson_7_3_4s_plans(sm):
    assert score(sm, weighted(sm, 1, 0)) == (24260, pytest.approx(10576.65, abs=0.01))
    assert score(sm, weighted(sm, 0, 1)) == (18886, pytest.approx(16086.12, abs=0.01))


def test_only_the_ratio_matters(sm):
    plans = [weighted(sm, a, b) for a, b in ((0.5, 0.5), (3, 3), (0.2, 0.8))]
    assert plans[0] == plans[1] == plans[2]
    assert score(sm, plans[0])[0] == 22870


def test_risk_in_millions_turns_50_50_into_the_npv_plan(sm):
    assert score(sm, weighted(sm, 0.5, 0.5 / 1000))[0] == 24260


def test_the_plan_jumps_at_the_break_even_share(sm):
    a, b = score(sm, weighted(sm, 0.60, 0.40)), score(sm, weighted(sm, 0.61, 0.39))
    assert (a[0], b[0]) == (22870, 23573)
    share = (a[1] - b[1]) / ((b[0] - a[0]) + (a[1] - b[1]))
    assert 0.60 < share < 0.61


def test_no_share_reaches_the_planners_plan(sm):
    row = sm.model.add_linear_constraint(sm.npv_of() >= 0.95 * 24260, name="npv_floor")
    sm.model.maximize(sm.risk_of())
    q = score(sm, plan_of(sm, solve_highs(sm.model)))
    sm.model.delete_linear_constraint(row)
    assert q[0] == 23104
    a, b = score(sm, weighted(sm, 0.5, 0.5)), score(sm, weighted(sm, 0.61, 0.39))
    low = (a[1] - q[1]) / ((q[0] - a[0]) + (a[1] - q[1]))
    high = (q[1] - b[1]) / ((b[0] - q[0]) + (q[1] - b[1]))
    assert low > high
    for k in range(101):                                   # and no grid share returns it
        assert score(sm, weighted(sm, k / 100, 1 - k / 100)) != q


def test_the_lp_relaxation_answer_is_a_weighted_optimum():
    lp = build(generate("small"), integer=False)
    row = lp.model.add_linear_constraint(lp.npv_of() >= 23104, name="npv_floor")
    lp.model.maximize(lp.risk_of())
    result = solve_highs(lp.model)
    x = result.variable_values()
    npv = sum(lp.npv[k] * x[v] for k, v in lp.x.items())
    risk = result.objective_value()
    mu = -result.dual_values(row)
    lp.model.delete_linear_constraint(row)
    lp.model.maximize(mu * lp.npv_of() + lp.risk_of())
    assert solve_highs(lp.model).termination.reason == mathopt.TerminationReason.OPTIMAL
    assert solve_highs(lp.model).objective_value() == pytest.approx(mu * npv + risk, rel=1e-7)
    assert risk > 16086.12
