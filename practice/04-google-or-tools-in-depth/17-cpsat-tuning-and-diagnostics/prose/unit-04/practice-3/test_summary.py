import pytest

from summary import read_summary, relative_gap

# Made-up summaries of a depot-siting model, shaped like CP-SAT 9.15's.


def summary(status: str, objective: str, bound: str) -> str:
    return ("#Done    1.20s main\n\nLRAT_status: NA\nCpSolverResponse summary:\n"
            f"status: {status}\nobjective: {objective}\nbest_bound: {bound}\nintegers: 120\n"
            "booleans: 96\nconflicts: 412\nbranches: 9031\nwalltime: 1.21\nusertime: 1.21\n"
            "deterministic_time: 0.734\ngap_integral: 2.5\nsolution_fingerprint: 0x9f2e\n")


def test_the_summary_block_is_read_as_key_value_pairs():
    fields = read_summary(summary("FEASIBLE", "8400", "8820"))
    assert fields.get("status") == "FEASIBLE"
    assert fields.get("branches") == "9031"
    assert fields.get("solution_fingerprint") == "0x9f2e"
    assert len(fields) == 12


def test_the_gap_of_a_stopped_maximization():
    assert relative_gap(summary("FEASIBLE", "8400", "8820")) == pytest.approx(0.05)
    assert relative_gap(summary("OPTIMAL", "8820", "8820")) == 0.0


def test_the_gap_of_a_stopped_minimization_is_positive():
    assert relative_gap(summary("FEASIBLE", "5000", "4750")) == pytest.approx(0.05)


def test_an_objective_of_zero_divides_by_one():
    assert relative_gap(summary("FEASIBLE", "0", "3")) == pytest.approx(3.0)
