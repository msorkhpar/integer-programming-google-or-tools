from ortools.math_opt.python import mathopt

from shortlist import shortlist

S = mathopt.SolverType


def freight(kind: str) -> mathopt.Model:
    """Trucks (integer) and tons shipped (continuous) on two lanes, a freight company's week."""
    model = mathopt.Model(name=f"freight-{kind}")
    integer_trucks = kind in ("milp", "mixed")
    integer_tons = kind == "milp"
    t1 = model.add_variable(lb=0, ub=6, is_integer=integer_trucks, name="trucks_north")
    t2 = model.add_variable(lb=0, ub=6, is_integer=integer_trucks, name="trucks_south")
    w1 = model.add_variable(lb=0, ub=90, is_integer=integer_tons, name="tons_north")
    w2 = model.add_variable(lb=0, ub=90, is_integer=integer_tons, name="tons_south")
    model.add_linear_constraint(w1 <= 14 * t1, name="load_north")
    model.add_linear_constraint(w2 <= 14 * t2, name="load_south")
    model.add_linear_constraint(t1 + t2 <= 7, name="fleet")
    model.maximize(5 * w1 + 4 * w2 - 30 * t1 - 25 * t2)
    return model


def test_an_lp_goes_to_every_solver_but_cp_sat():
    assert shortlist(freight("lp")) == [S.GLOP, S.PDLP, S.HIGHS, S.GSCIP]


def test_an_all_integer_model_goes_to_the_three_milp_solvers():
    assert shortlist(freight("milp")) == [S.HIGHS, S.GSCIP, S.CP_SAT]


def test_every_shortlisted_solver_solves_the_model():
    for kind in ("lp", "milp", "mixed"):
        model = freight(kind)
        solvers = shortlist(model)
        assert solvers
        values = set()
        for solver in solvers:
            try:
                result = mathopt.solve(model, solver)
            except Exception:                   # a refusal: this solver should not be on the list
                result = None
            assert result is not None, f"{solver.name} refused the {kind} model"
            assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
            values.add(round(result.objective_value(), 2))
        assert len(values) == 1


def test_a_mixed_model_is_kept_from_cp_sat():
    assert shortlist(freight("mixed")) == [S.HIGHS, S.GSCIP]


def test_an_lp_that_needs_duals_skips_scip():
    assert shortlist(freight("lp"), need_duals=True) == [S.GLOP, S.PDLP, S.HIGHS]


def test_a_milp_that_needs_duals_has_no_solver():
    assert shortlist(freight("mixed"), need_duals=True) == []
