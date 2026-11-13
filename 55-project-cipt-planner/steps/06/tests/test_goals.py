"""Lesson 14.2.5: the trade between NPV and the risk a plan removes."""

from cipt.data import load_request
from cipt.goals import frontier
from cipt.solve import solve
from conftest import export, row

TWO = (2027, 2028)


def asset(cof):
    return {"id": f"A{cof}", "age": 5, "weibull_beta": 1.0, "weibull_eta": 10.0, "cof": cof}


def three(**settings):
    """Two of three projects fit: A is worth the most NPV, C removes the most risk."""
    return export([row("A", (50,), 300, asset=asset(100)), row("B", (50,), 200, asset=asset(2000)),
                   row("C", (50,), 100, asset=asset(4000))], years=TWO, budget={2027: 100, 2028: 0},
                  **settings)


def test_frontier_runs_from_best_npv_to_most_risk_removed():
    points = frontier(load_request(three()), points=3)
    assert [round(p.npv) for p in points] == [500, 400, 300]


def test_frontier_finds_the_plan_between_the_ends():
    points = frontier(load_request(three()), points=3)
    assert [p.plan.funded for p in points] == [("A", "B"), ("A", "C"), ("B", "C")]


def test_no_frontier_point_is_dominated():
    points = frontier(load_request(three()), points=5)
    assert len(points) >= 2
    assert all(not (p.npv >= q.npv and p.risk >= q.risk) for p in points for q in points if p is not q)


def test_tied_npv_end_takes_the_most_risk():
    # A and B are worth the same NPV; only one fits. The NPV end of the frontier must be B.
    raw = export([row("A", (50,), 300, asset=asset(100)), row("B", (50,), 300, asset=asset(3000))],
                 years=TWO, budget={2027: 50, 2028: 0})
    assert [p.plan.funded for p in frontier(load_request(raw), points=2)][:1] == [("B",)]


def test_risk_floor_is_respected():
    plan = solve(load_request(three(risk_floor=300)))
    assert (plan.funded, round(plan.npv)) == (("A", "C"), 400)
