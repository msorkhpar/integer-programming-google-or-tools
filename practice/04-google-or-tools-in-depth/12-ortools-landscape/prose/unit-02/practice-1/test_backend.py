from backend import pick_backend


def test_a_missing_commercial_solver_is_skipped():
    assert pick_backend(["GUROBI", "SCIP"]) == "SCIP"
    assert pick_backend(["CPLEX", "XPRESS", "CBC"]) == "CBC"


def test_the_first_present_mip_solver_wins():
    assert pick_backend(["CBC", "SCIP", "HIGHS"]) == "CBC"
    assert pick_backend(["HIGHS", "CBC"]) == "HIGHS"


def test_an_lp_only_solver_is_skipped():
    assert pick_backend(["GLOP", "CBC"]) == "CBC"
    assert pick_backend(["GUROBI", "CLP", "PDLP", "SCIP"]) == "SCIP"


def test_no_present_mip_solver_gives_none():
    assert pick_backend(["GUROBI", "XPRESS"]) is None
    assert pick_backend([]) is None
