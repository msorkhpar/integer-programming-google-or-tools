from ortools.math_opt.python import mathopt

from tracker import make_tracker

EVENT = mathopt.Event.MIP_SOLUTION


def crates():
    """A warehouse picking crates, not the lesson's portfolio."""
    model = mathopt.Model()
    x = [model.add_binary_variable(name=f"crate{i}") for i in range(4)]
    return model, x


def report(callback, solution):
    return callback(mathopt.CallbackData(event=EVENT, solution=solution))


def test_improving_solutions_are_recorded():
    _, x = crates()
    callback, history = make_tracker({x[0]: 5.0, x[1]: 3.0}, maximize=True)
    first = report(callback, {x[0]: 0.0, x[1]: 1.0})
    report(callback, {x[0]: 1.0, x[1]: 1.0})
    assert history == [3.0, 8.0]
    assert isinstance(first, mathopt.CallbackResult) and first.terminate is False


def test_a_real_solve_ends_at_the_optimum():
    model, x = crates()
    weights, values = [4, 3, 2, 5], [9.0, 7.0, 4.0, 10.0]
    model.add_linear_constraint(sum(w * v for w, v in zip(weights, x)) <= 9)
    model.maximize(sum(c * v for c, v in zip(values, x)))
    callback, history = make_tracker(dict(zip(x, values)), maximize=True)
    reg = mathopt.CallbackRegistration(events={EVENT})
    result = mathopt.solve(model, mathopt.SolverType.GSCIP, callback_reg=reg, cb=callback)
    assert history and abs(max(history) - result.objective_value()) < 1e-6


def test_a_worse_solution_keeps_the_best():
    _, x = crates()
    callback, history = make_tracker({x[0]: 5.0, x[1]: 3.0}, maximize=True)
    for solution in ({x[0]: 1.0, x[1]: 1.0}, {x[0]: 0.0, x[1]: 1.0}):
        report(callback, solution)
    assert history == [8.0, 8.0]


def test_a_minimization_keeps_the_lowest():
    _, x = crates()
    callback, history = make_tracker({x[2]: 4.0, x[3]: 6.0}, maximize=False)
    for solution in ({x[2]: 1.0, x[3]: 1.0}, {x[2]: 1.0, x[3]: 0.0}, {x[2]: 0.0, x[3]: 1.0}):
        report(callback, solution)
    assert history == [10.0, 4.0, 4.0]
