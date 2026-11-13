from ortools.math_opt.python import mathopt

from cuts import build, cut_table

# A school district's summer repairs, not the lesson's portfolio: name -> (value, cost $k).
REPAIRS = {"roof": (90, 60), "boiler": (70, 50), "windows": (40, 30), "lab": (55, 45),
           "ramp": (30, 15), "gym": (25, 20)}
BUDGET = 150


def fresh(limit: float) -> float:
    model, _, _ = build(REPAIRS, limit)
    return mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value()


def test_one_value_per_cut_matching_a_fresh_solve():
    model, _, row = build(REPAIRS, BUDGET)
    values = cut_table(model, row, [0.0, 0.3])
    assert len(values) == 2
    assert abs(values[0] - fresh(BUDGET)) < 1e-6
    assert abs(values[1] - fresh(0.7 * BUDGET)) < 1e-6


def test_the_model_is_not_rebuilt():
    model, _, row = build(REPAIRS, BUDGET)
    values = cut_table(model, row, [0.1])
    assert len(values) == 1
    assert model.get_num_linear_constraints() == 1 and model.get_num_variables() == len(REPAIRS)


def test_each_cut_is_taken_from_the_original_limit():
    model, _, row = build(REPAIRS, BUDGET)
    values = cut_table(model, row, [0.2, 0.1])
    assert len(values) == 2 and abs(values[1] - fresh(0.9 * BUDGET)) < 1e-6


def test_the_limit_is_back_afterwards():
    model, _, row = build(REPAIRS, BUDGET)
    values = cut_table(model, row, [0.2, 0.4])
    assert len(values) == 2 and row.upper_bound == BUDGET
