"""The module 22 examples: the instance set, the solver runs, the shifted geometric mean and the license checks."""

import math

import pytest

from instances import build_cpsat, build_mathopt, instance_set
from license_route import log_line, route
from model_sizes import LIMITS, Limit
from sgm import shifted_geometric_mean
from solvers import run


@pytest.fixture(scope="module")
def instances():
    return {inst.name: inst for inst in instance_set()}


def test_the_instance_set_has_six_slices_with_scaled_budgets(instances):
    assert sorted(instances) == sorted(f"{p}-{s}" for p in ("transmission", "distribution", "vegetation")
                                       for s in (2027, 1))
    for inst in instances.values():
        ids = {p.project_id for p in inst.projects}
        assert all(c.parent in ids for c in inst.children())
        assert all(b >= 0 for b in inst.budget.values())


def test_the_three_builders_make_the_same_rows(instances):
    inst = instances["vegetation-1"]
    model, x = build_mathopt(inst)
    cp, _ = build_cpsat(inst)
    assert len(x) == len(inst.projects)
    assert len(list(model.linear_constraints())) == len(cp.proto.constraints)


def test_every_solver_finds_the_same_optimum_and_repeats(instances):
    inst = instances["vegetation-1"]
    runs = {s: run(s, inst, 1) for s in ("HiGHS", "SCIP", "CP-SAT", "CBC")}
    assert {round(r.objective) for r in runs.values()} == {13833}
    assert all(r.status == "optimal" for r in runs.values())
    again = run("HiGHS", inst, 1)
    assert again.work == runs["HiGHS"].work


def test_a_gap_target_stops_early_with_the_harness_gap_within_it(instances):
    r = run("HiGHS", instances["distribution-2027"], 1, gap=0.01)
    assert r.status == "gap reached"
    assert r.gap() <= 0.01


def test_settings_reach_only_the_mathopt_solvers(instances):
    with pytest.raises(ValueError):
        run("CP-SAT", instances["vegetation-1"], 1, presolve=None)


def test_the_shifted_geometric_mean_follows_mittelmanns_form():
    assert shifted_geometric_mean([2.0, 8.0], 0.0) == pytest.approx(4.0)
    assert shifted_geometric_mean([7.0, 7.0], 10.0) == pytest.approx(7.0)
    assert shifted_geometric_mean([0.01, 0.1], 0.0) == pytest.approx(1.0)
    assert shifted_geometric_mean([0.5, 40.0], 10.0) == pytest.approx(math.sqrt(10.5 * 50.0) - 10.0)


def test_the_harness_counts_cpsat_where_the_clamp_never_decides(instances):
    from harness import SHIFT, UNIT, counted

    assert all(shift >= 1 for shift in SHIFT.values())
    easy = run("CP-SAT", instances["vegetation-2027"], 1)
    assert easy.work["det_time"] < 1
    assert counted(easy, "det_time") == pytest.approx(easy.work["det_time"] * UNIT["det_time"][1])
    assert counted(easy, "det_time") >= 1


def test_the_free_tier_limits_apply_each_cap():
    gurobi, cplex, xpress = LIMITS
    assert gurobi.fits(2000, 2000) and not gurobi.fits(2001, 10)
    assert cplex.fits(1000, 1000) and not cplex.fits(887, 1001)
    assert xpress.fits(4000, 1000) and not xpress.fits(4000, 1001)
    assert Limit("none", None, None, None).fits(10**6, 10**6)


def test_the_license_log_names_settings_but_never_values():
    settings = {"WLSACCESSID": "id-value", "WLSSECRET": "secret-value", "LICENSEID": "42"}
    line = log_line(settings, set())
    assert "WLS" in line and "secret-value" not in line and "id-value" not in line
    assert route({"WLSACCESSID": "x"}, set()).startswith("broken WLS setup")
    assert route({"GRB_LICENSE_FILE": "/l/g.lic"}, set()).startswith("GRB_LICENSE_FILE set, but nothing mounted")
