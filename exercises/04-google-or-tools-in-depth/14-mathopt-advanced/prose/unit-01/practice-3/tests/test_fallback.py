from ortools.math_opt.python import mathopt

from fallback import solve_first

S = mathopt.SolverType


def depot_model(with_indicator: bool) -> mathopt.Model:
    """A bus depot's charger plan, not the lesson's portfolio."""
    model = mathopt.Model(name="depot")
    open_ = model.add_binary_variable(name="open")
    load = model.add_variable(lb=0, ub=80, name="load")
    if with_indicator:
        model.add_indicator_constraint(indicator=open_, activate_on_zero=True, implied_constraint=load <= 20)
    else:
        model.add_linear_constraint(load <= 20 + 60 * open_)
    model.maximize(load - 30 * open_)
    return model


def test_an_indicator_model_falls_through_to_scip():
    solver, result, reasons = solve_first(depot_model(True), [S.HIGHS, S.CP_SAT, S.GSCIP])
    assert solver == S.GSCIP
    assert result is not None and abs(result.objective_value() - 50) < 1e-6
    assert set(reasons) == {"HIGHS", "CP_SAT"}


def test_a_plain_model_is_solved_by_the_first_solver():
    solver, result, reasons = solve_first(depot_model(False), [S.HIGHS, S.GSCIP])
    assert solver == S.HIGHS and reasons == {}
    assert result is not None and abs(result.objective_value() - 50) < 1e-6


def test_a_reason_is_the_solver_s_own_words():
    _, _, reasons = solve_first(depot_model(True), [S.HIGHS, S.GSCIP])
    assert "does not support indicator constraints" in reasons.get("HIGHS", "")


def test_no_solver_accepts():
    solver, result, reasons = solve_first(depot_model(True), [S.HIGHS, S.GLOP])
    assert solver is None and result is None
    assert set(reasons) == {"HIGHS", "GLOP"}
    assert "integer variables" in reasons["GLOP"]
