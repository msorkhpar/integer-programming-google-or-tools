from ortools.math_opt.python import mathopt

from highs_settings import highs_parameters

# Five loads, their weights (t) and values; one truck of 10 t.
LOADS = {"L1": (4, 9), "L2": (3, 7), "L3": (5, 10), "L4": (2, 4), "L5": (6, 11)}


def solve(params: mathopt.SolveParameters) -> mathopt.SolveResult:
    model = mathopt.Model()
    x = {k: model.add_binary_variable(name=k) for k in LOADS}
    model.add_linear_constraint(sum(w * x[k] for k, (w, _) in LOADS.items()) <= 10, name="truck")
    model.maximize(sum(v * x[k] for k, (_, v) in LOADS.items()))
    return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)


def test_the_seed_and_the_node_limit_are_set_and_the_solve_runs():
    params = highs_parameters(seed=3, threads=1, nodes=500)
    assert params.random_seed == 3
    assert params.node_limit == 500
    result = solve(params)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    assert round(result.objective_value()) == 21


def test_the_thread_count_goes_to_highs_own_options():
    params = highs_parameters(seed=3, threads=1, nodes=500)
    assert params.threads is None
    assert params.highs.int_options["threads"] == 1


def test_no_clock_limit_is_set():
    params = highs_parameters(seed=5, threads=1, nodes=200)
    assert params.time_limit is None
    assert params.node_limit == 200
