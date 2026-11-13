from port import set_objective_n_args


def level(name, priority, maximize=True, abs_tol=1.0, rel_tol=0.01):
    return {"name": name, "priority": priority, "maximize": maximize, "abs_tol": abs_tol, "rel_tol": rel_tol}


def gurobi_order(args):
    """Names in the order Gurobi optimizes them: the highest priority first."""
    return [a["name"] for a in sorted(args, key=lambda a: -a["priority"])]


def test_maximized_levels_keep_their_order_names_and_tolerances():
    levels = [level("urgent", 0, abs_tol=0.5, rel_tol=0.02), level("staff", 1, abs_tol=1.0, rel_tol=0.0),
              level("requests", 2, abs_tol=3.0, rel_tol=0.1)]
    args = set_objective_n_args(levels)
    assert gurobi_order(args) == ["urgent", "staff", "requests"]
    assert [a["index"] for a in args] == [0, 1, 2]
    assert [a["weight"] for a in args] == [1, 1, 1]
    assert [(a["abstol"], a["reltol"]) for a in args] == [(0.5, 0.02), (1.0, 0.0), (3.0, 0.1)]


def test_a_minimized_level_gets_a_negative_weight():
    args = set_objective_n_args([level("urgent", 0), level("overtime", 1, maximize=False)])
    assert gurobi_order(args) == ["urgent", "overtime"]
    assert [a["weight"] for a in args] == [1, -1]


def test_an_unset_absolute_tolerance_means_no_loss():
    args = set_objective_n_args([level("urgent", 0, abs_tol=None, rel_tol=None), level("staff", 1)])
    assert gurobi_order(args) == ["urgent", "staff"]
    assert (args[0]["abstol"], args[0]["reltol"]) == (0.0, 0.0)


def test_priorities_need_not_be_consecutive_or_sorted():
    args = set_objective_n_args([level("requests", 7), level("urgent", 0), level("staff", 3)])
    assert gurobi_order(args) == ["urgent", "staff", "requests"]
    assert [a["index"] for a in args] == [0, 1, 2]
