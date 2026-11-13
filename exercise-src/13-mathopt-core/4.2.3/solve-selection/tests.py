import pandas as pd
import pytest
from ortools.math_opt.python import mathopt

from selection import solve_selection

S = mathopt.SolverType

# A parks department's playground renovations, not the lesson's portfolio.
PARKS = pd.DataFrame({
    "project_id": ["Elm", "Oak", "Ash", "Fir", "Yew", "Bay", "Gum"],
    "cost":       [42,    35,    28,    51,    19,    33,    24],
    "value":      [60,    44,    39,    70,    21,    40,    30],
    "must_do":    [False] * 7,
})
SAFETY = PARKS.assign(must_do=PARKS["project_id"] == "Yew")     # Yew's fencing is safety work


def best_by_hand(df, budget):
    """Every subset of the seven projects: the best value and its ids, keeping the must-dos."""
    best = (-1.0, [])
    rows = list(df.itertuples())
    for mask in range(1 << len(rows)):
        pick = [r for k, r in enumerate(rows) if mask >> k & 1]
        if any(r.must_do for r in rows if r not in pick):
            continue
        if sum(r.cost for r in pick) <= budget:
            value = float(sum(r.value for r in pick))
            if value > best[0]:
                best = (value, sorted(r.project_id for r in pick))
    return best


def raised(call):
    """(exception type, message) of what the call raised, or (None, None) if it raised nothing."""
    try:
        call()
    except Exception as error:
        return type(error), str(error)
    return None, None


def test_every_milp_solver_returns_the_same_best_plan():
    want = best_by_hand(PARKS, 121)
    for solver in (S.HIGHS, S.GSCIP, S.CP_SAT):
        value, chosen = solve_selection(PARKS, 121, solver)
        assert value == pytest.approx(want[0])
        assert chosen == want[1]


def test_the_plan_fits_the_budget():
    value, chosen = solve_selection(PARKS, 121, S.HIGHS)
    assert chosen
    assert PARKS.set_index("project_id").loc[chosen, "cost"].sum() <= 121


def test_must_do_projects_are_always_funded():
    value, chosen = solve_selection(SAFETY, 121, S.HIGHS)
    assert "Yew" in chosen
    assert value == pytest.approx(best_by_hand(SAFETY, 121)[0])


def test_projects_are_funded_whole():
    value, chosen = solve_selection(PARKS, 60, S.HIGHS)
    assert value == pytest.approx(best_by_hand(PARKS, 60)[0])


def test_an_lp_only_solver_is_refused_with_a_value_error():
    for solver in (S.GLOP, S.PDLP):
        kind, message = raised(lambda: solve_selection(PARKS, 121, solver))
        assert kind is ValueError
        assert solver.name in message


def test_an_impossible_budget_raises_runtime_error():
    kind, message = raised(lambda: solve_selection(SAFETY, 10, S.HIGHS))
    assert kind is RuntimeError
    assert "INFEASIBLE" in message
