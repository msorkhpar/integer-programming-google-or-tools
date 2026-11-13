from ortools.math_opt.python import mathopt

from hinting import build, hint_params

# A courier's routes, not the lesson's portfolio: name -> (profit, vans needed).
ROUTES = {"north": (40, 2), "south": (30, 1), "east": (25, 2), "west": (20, 1), "harbor": (15, 1),
          "ring": (33, 3), "airport": (28, 2), "mill": (12, 1), "docks": (22, 2), "campus": (18, 1),
          "hills": (26, 3), "market": (17, 1)}
LAST_WEEK = {"north", "south", "west", "campus"}                  # 5 vans, profit 108


def hint_values(params) -> list[dict[str, float]]:
    return [{v.name: val for v, val in h.variable_values.items()} for h in params.solution_hints]


def test_a_complete_hint_of_a_feasible_plan_is_used():
    model, y = build(ROUTES, 6)
    log: list[str] = []
    mathopt.solve(model, mathopt.SolverType.HIGHS, model_params=hint_params(y, LAST_WEEK, True),
                  msg_cb=mathopt.list_message_callback(log))
    assert any("MIP start solution is feasible" in line for line in log)


def test_a_partial_hint_holds_the_chosen_routes_at_one():
    _, y = build(ROUTES, 6)
    hints = hint_values(hint_params(y, LAST_WEEK, False))
    assert len(hints) == 1
    assert all(hints[0].get(f"y_{r}") == 1.0 for r in LAST_WEEK)


def test_a_complete_hint_sets_the_other_routes_to_zero():
    _, y = build(ROUTES, 6)
    hints = hint_values(hint_params(y, LAST_WEEK, True))
    assert hints == [{f"y_{r}": 1.0 if r in LAST_WEEK else 0.0 for r in ROUTES}]


def test_a_partial_hint_leaves_the_other_routes_out():
    _, y = build(ROUTES, 6)
    hints = hint_values(hint_params(y, LAST_WEEK, False))
    assert hints == [{"y_north": 1.0, "y_south": 1.0, "y_west": 1.0, "y_campus": 1.0}]
