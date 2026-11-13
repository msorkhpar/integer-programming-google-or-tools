import pytest

from harness import benchmark, shifted_geometric_mean

WORK = {
    ("Fennec", "depot-a", 1): (True, 400.0), ("Fennec", "depot-b", 1): (True, 9000.0),
    ("Fennec", "depot-a", 2): (True, 1600.0), ("Fennec", "depot-b", 2): (True, 7000.0),
    ("Serval", "depot-a", 1): (True, 900.0), ("Serval", "depot-b", 1): (True, 2500.0),
    ("Serval", "depot-a", 2): (True, 1100.0), ("Serval", "depot-b", 2): (False, 50000.0),
}


def table(solver, instance, seed):
    return WORK[solver, instance, seed]


def test_each_solver_gets_the_mean_of_its_runs():
    result = benchmark(table, ["Fennec"], ["depot-a", "depot-b"], [1], 100.0, 1e6)
    assert result["Fennec"]["runs"] == 2
    assert result["Fennec"]["solved"] == 2
    assert result["Fennec"]["repeat"] is True
    assert result["Fennec"]["sgm"] == pytest.approx(shifted_geometric_mean([400.0, 9000.0], 100.0))


def test_every_seed_is_an_observation():
    result = benchmark(table, ["Fennec"], ["depot-a", "depot-b"], [1, 2], 100.0, 1e6)
    assert result["Fennec"]["runs"] == 4
    assert result["Fennec"]["sgm"] == pytest.approx(shifted_geometric_mean([400.0, 1600.0, 9000.0, 7000.0], 100.0))


def test_an_unsolved_run_counts_at_the_cap():
    result = benchmark(table, ["Serval"], ["depot-a", "depot-b"], [1, 2], 100.0, 1e6)
    assert result["Serval"]["solved"] == 3
    assert result["Serval"]["sgm"] == pytest.approx(shifted_geometric_mean([900.0, 1100.0, 2500.0, 1e6], 100.0))


def test_a_cell_that_does_not_repeat_is_flagged():
    calls = {"n": 0}

    def drifting(solver, instance, seed):
        calls["n"] += 1
        solved, work = WORK[solver, instance, seed]
        return solved, work + (calls["n"] % 2 if instance == "depot-b" else 0)

    assert benchmark(drifting, ["Fennec"], ["depot-a", "depot-b"], [1], 100.0, 1e6)["Fennec"]["repeat"] is False
    assert benchmark(table, ["Fennec"], ["depot-a", "depot-b"], [1], 100.0, 1e6)["Fennec"]["repeat"] is True
