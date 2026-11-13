import pytest

from footer import read_footer

HEADER = [
    "LP pumps has 6 rows; 9 cols; 21 nonzeros",
    "Coefficient ranges:",
    "  Matrix  [1e+00, 8e+00]",
    "Presolving model",
    "Presolve reductions: rows 5(-1); columns 9(-0); nonzeros 19(-2) ",
]
OPTIMAL = HEADER + [
    "Using EKK dual simplex solver - serial",
    "  Iteration        Objective     Infeasibilities num(sum)",
    "          0    -1.0000000000e+01 Ph1: 2(3.5) 0s",
    "          7     4.1250000000e+02 Pr: 0(0) 0s",
    "Model name          : pumps",
    "Model status        : Optimal",
    "Simplex   iterations: 7",
    "Objective value     :  4.1250000000e+02",
    "P-D objective error :  0.0000000000e+00",
    "HiGHS run time      :          0.01",
]
BARRIER = HEADER + [
    "Ipx: IPM       optimal",
    "Ipx: Crossover optimal",
    "Model name          : pumps",
    "Model status        : Optimal",
    "IPM       iterations: 11",
    "Objective value     :  4.1250000000e+02",
    "HiGHS run time      :          0.02",
]
INFEASIBLE = HEADER[:4] + [
    "Problem status detected on presolve: Infeasible",
    "Model name          : pumps",
    "Model status        : Infeasible",
    "Objective value     :  0.0000000000e+00",
    "HiGHS run time      :          0.00",
]
UNBOUNDED = HEADER[:4] + [
    "Problem status detected on presolve: Primal infeasible or unbounded",
    "Model name          : pumps",
    "Model status        : Unbounded",
    "Simplex   iterations: 4",
    "Objective value     :  9.0000000000e+02",
    "HiGHS run time      :          0.00",
]


def test_an_optimal_log_gives_its_status_iterations_and_objective():
    assert read_footer(OPTIMAL) == {"status": "Optimal", "iterations": {"Simplex": 7}, "objective": pytest.approx(412.5)}


def test_a_barrier_log_counts_its_iterations_under_their_own_kind():
    assert read_footer(BARRIER) == {"status": "Optimal", "iterations": {"IPM": 11}, "objective": pytest.approx(412.5)}


def test_an_infeasible_log_has_no_objective_and_no_iterations():
    assert read_footer(INFEASIBLE) == {"status": "Infeasible", "iterations": {}, "objective": None}


def test_an_unbounded_log_has_iterations_but_no_objective():
    assert read_footer(UNBOUNDED) == {"status": "Unbounded", "iterations": {"Simplex": 4}, "objective": None}
