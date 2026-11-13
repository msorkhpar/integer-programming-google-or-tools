from ortools.math_opt.python import mathopt

from stopper import stop_at


def stops(target: float, primal: float, dual: float) -> bool:
    data = mathopt.CallbackData(event=mathopt.Event.MIP_SOLUTION,
                                mip_stats=mathopt.MipStats(primal_bound=primal, dual_bound=dual))
    return stop_at(target)(data).terminate


def test_a_small_gap_stops_the_solve():
    assert stops(0.03, primal=1000.0, dual=1020.0) is True          # 2%


def test_a_large_gap_lets_it_run():
    assert stops(0.03, primal=1000.0, dual=1050.0) is False         # 5%
    assert stops(0.06, primal=1000.0, dual=1050.0) is True


def test_a_minimization_measures_the_gap_the_same_way():
    assert stops(0.03, primal=1000.0, dual=950.0) is False          # 5%, bound below
    assert stops(0.03, primal=1000.0, dual=980.0) is True           # 2%
