import pytest

from converged import converged_at, table_rows

HEAD = " iter# kkt_pass   time | rel_prim_res rel_dual_res      rel_gap |   prim_resid   dual_resid      obj_gap"


def row(iteration: int, prim: float, dual: float, gap: float) -> str:
    return (f"{iteration:6d} {iteration + 1:8.1f}    0.0 | {prim:12.5e} {dual:12.5e} {gap:12.5e} "
            f"|      1.00000      2.00000      3.00000")


LOG = [
    "Solving with PDLP parameters: example",
    "There are 120 variables, 45 constraints, and 380 constraint matrix nonzeros.",
    HEAD,
    row(0, 3.2e-2, 0.9, 0.0),
    row(32, 4.1e-4, 2.2e-4, 1.5e-4),
    row(64, 8.0e-6, 3.0e-6, -2.0e-6),
    row(96, 5.0e-8, 7.0e-9, 9.0e-9),
    "Termination reason: TERMINATION_REASON_OPTIMAL",
    "Final solution stats:",
    HEAD,
    row(96, 5.0e-8, 7.0e-9, 9.0e-9),
]


def test_the_table_rows_are_read_and_the_header_is_skipped():
    rows = table_rows(LOG)
    assert [r[0] for r in rows] == [0, 32, 64, 96, 96]
    assert rows[2] == (64, pytest.approx(8.0e-6), pytest.approx(3.0e-6), pytest.approx(-2.0e-6))


def test_convergence_is_the_first_row_within_tolerance():
    assert converged_at(LOG, 1e-5) == 64
    assert converged_at(LOG, 1e-6) == 96


def test_a_large_negative_gap_is_not_converged():
    log = [HEAD, row(0, 1e-7, 1e-7, -0.4), row(50, 1e-7, 1e-7, 1e-8)]
    assert converged_at(log, 1e-6) == 50


def test_all_three_measures_must_be_within_tolerance():
    log = [HEAD, row(0, 1e-7, 1e-7, 0.3), row(40, 1e-7, 0.2, 1e-8), row(80, 1e-7, 1e-7, 1e-8)]
    assert converged_at(log, 1e-6) == 80


def test_a_run_that_never_gets_there_gives_none():
    assert converged_at(LOG, 1e-9) is None
