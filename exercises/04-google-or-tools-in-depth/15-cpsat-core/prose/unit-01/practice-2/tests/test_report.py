import random

from ortools.sat.python import cp_model

from report import report


def knapsack(capacity: int, n: int = 30):
    """A loading problem of n crates; the values and weights are invented for the tests."""
    rng = random.Random(4)
    values = [rng.randint(5, 40) for _ in range(n)]
    weights = [rng.randint(3, 20) for _ in range(n)]
    model = cp_model.CpModel()
    x = {f"crate{i:02d}": model.new_bool_var(f"crate{i:02d}") for i in range(n)}
    model.add(sum(w * v for w, v in zip(weights, x.values())) <= capacity)
    model.maximize(sum(c * v for c, v in zip(values, x.values())))
    return model, x


def test_an_optimal_plan_is_read_and_marked_proven():
    model = cp_model.CpModel()
    x = {name: model.new_bool_var(name) for name in ("a", "b", "c")}
    model.add(2 * x["a"] + 3 * x["b"] + 4 * x["c"] <= 5)
    model.maximize(3 * x["a"] + 4 * x["b"] + 5 * x["c"])
    assert report(model, x) == {"status": "OPTIMAL", "plan": ["a", "b"], "objective": 7, "proven": True,
                                "reason": ""}


def test_an_infeasible_model_has_no_plan():
    model = cp_model.CpModel()
    x = {name: model.new_bool_var(name) for name in ("a", "b")}
    model.add(x["a"] + x["b"] >= 3)
    model.maximize(x["a"])
    assert report(model, x) == {"status": "INFEASIBLE", "plan": None, "objective": None, "proven": False,
                                "reason": ""}


def test_a_plan_from_a_stopped_search_is_read_but_not_proven():
    model, x = knapsack(100)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.stop_after_first_solution = True
    solver.parameters.cp_model_presolve = False
    solver.parameters.linearization_level = 0
    answer = report(model, x, solver)
    assert answer["status"] == "FEASIBLE"
    assert answer["proven"] is False
    assert answer["plan"] and answer["objective"] == 202


def test_an_invalid_model_says_why():
    model = cp_model.CpModel()
    x = {"a": model.new_bool_var("a")}
    spend = model.new_int_var(0, 2**62, "spend")
    model.add(spend >= 1)
    answer = report(model, x)
    assert answer["status"] == "MODEL_INVALID"
    assert answer["plan"] is None
    assert "spend" in answer["reason"]


def test_a_model_without_an_objective_has_no_objective_value():
    model = cp_model.CpModel()
    x = {name: model.new_bool_var(name) for name in ("a", "b")}
    model.add_exactly_one(x.values())
    model.add(x["a"] == 0)
    assert report(model, x) == {"status": "OPTIMAL", "plan": ["b"], "objective": None, "proven": True,
                                "reason": ""}
