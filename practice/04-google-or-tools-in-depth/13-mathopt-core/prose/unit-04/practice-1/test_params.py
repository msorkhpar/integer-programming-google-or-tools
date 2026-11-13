import datetime

from ortools.math_opt.python import mathopt

from params import params_for

S = mathopt.SolverType
ALL = (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT)


def pairing(integer: bool) -> mathopt.Model:
    """Choose crew pairings to cover four flights at least cost: an airline's tiny set cover."""
    cost = [7, 5, 6, 4, 8, 3]
    covers = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 1, 2, 3), (2,)]
    model = mathopt.Model(name="pairing")
    y = [model.add_variable(lb=0, ub=1, is_integer=integer, name=f"p{k}") for k in range(len(cost))]
    for flight in range(4):
        model.add_linear_constraint(mathopt.fast_sum(y[k] for k, c in enumerate(covers) if flight in c) >= 1,
                                    name=f"cover_{flight}")
    model.minimize(mathopt.fast_sum(c * v for c, v in zip(cost, y)))
    return model


def solved(solver: mathopt.SolverType, params: mathopt.SolveParameters) -> bool:
    """True when the solver ran with these parameters, False when it refused them."""
    model = pairing(integer=solver not in (S.GLOP, S.PDLP))
    try:
        mathopt.solve(model, solver, params=params)
    except Exception:
        return False
    return True


def test_time_and_gap_are_set_for_every_solver():
    for solver in ALL:
        p = params_for(solver, 45, 0.002, 4, 11)
        assert p.time_limit == datetime.timedelta(seconds=45)
        assert p.relative_gap_tolerance == 0.002


def test_scip_and_cp_sat_get_threads_and_seed():
    for solver in (S.GSCIP, S.CP_SAT):
        p = params_for(solver, 45, 0.002, 4, 11)
        assert (p.threads, p.random_seed) == (4, 11)
        assert solved(solver, p), solver.name


def test_highs_gets_no_threads():
    p = params_for(S.HIGHS, 45, 0.002, 4, 11)
    assert (p.threads, p.random_seed) == (None, 11)
    assert solved(S.HIGHS, p)


def test_pdlp_gets_no_seed():
    p = params_for(S.PDLP, 45, 0.002, 4, 11)
    assert (p.threads, p.random_seed) == (4, None)
    assert solved(S.PDLP, p)


def test_a_first_plan_stop_goes_only_to_milp_solvers():
    for solver in ALL:
        p = params_for(solver, 45, 0.002, 4, 11, first_plan=True)
        want = None if solver in (S.GLOP, S.PDLP) else 1
        assert p.solution_limit == want, solver.name
        assert solved(solver, p), solver.name
