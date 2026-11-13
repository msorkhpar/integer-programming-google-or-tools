from ortools.math_opt.python import mathopt

from without import build, objective_without

HIGHS = mathopt.SolverType.HIGHS
# A telecom operator's towers, not the lesson's portfolio: name -> (value per radio, cost, most radios).
TOWERS = {"hill": (9, 4, 1), "mall": (7, 3, 3), "port": (6, 2, 1), "farm": (3, 2, 1), "school": (5, 3, 1)}
BUDGET = 12


def optimum(model) -> float:
    return mathopt.solve(model, HIGHS).objective_value()


def test_ruling_out_gives_the_optimum_without_them():
    model, u = build(TOWERS, BUDGET)
    value = objective_without(model, [u["mall"], u["port"]], HIGHS)
    reference, v = build(TOWERS, BUDGET)
    v["mall"].upper_bound = v["port"].upper_bound = 0
    assert abs(value - optimum(reference)) < 1e-6


def test_the_model_is_unchanged_afterwards():
    model, u = build(TOWERS, BUDGET)
    base = optimum(model)
    value = objective_without(model, [u["hill"]], HIGHS)
    reference, v = build(TOWERS, BUDGET)
    v["hill"].upper_bound = 0
    assert abs(value - optimum(reference)) < 1e-6 and value < base
    assert model.get_num_variables() == len(TOWERS)
    assert abs(optimum(model) - base) < 1e-6


def test_each_bound_comes_back_to_its_own_value():
    model, u = build(TOWERS, BUDGET)
    value = objective_without(model, [u["mall"], u["hill"]], HIGHS)
    assert value > 0
    assert (u["mall"].upper_bound, u["hill"].upper_bound) == (3, 1)


def test_bounds_come_back_even_when_the_solve_fails():
    model, u = build(TOWERS, BUDGET)
    raised = False
    try:
        objective_without(model, [u["mall"]], mathopt.SolverType.GLOP)    # GLOP takes no integers
    except Exception:
        raised = True
    assert raised and u["mall"].upper_bound == 3
