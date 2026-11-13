"""The module 57 examples: every check runs on the CPU image; the ones marked requires_gpu() run only where a
GPU reached the container, and are skipped with a reason elsewhere."""

import subprocess
import sys
from pathlib import Path

import pytest
from ortools.pdlp import solvers_pb2

import lps
from fallback import agrees, solve_lp
from gpu import requires_gpu
from gpu_manifest import compare, manifest
from lps import cuopt, digest, gridcap_timing, highs, ortools_pdlp, relative_difference, transport, violation
from milp_gpu import check
from run_policy import Job, decide, jobs, run

SRC = Path(__file__).resolve().parents[1] / "src"


@pytest.fixture(scope="module")
def gridcap_lp():
    return gridcap_timing("small")[0]


@pytest.fixture(scope="module")
def exact(gridcap_lp):
    return highs(gridcap_lp, "simplex")


def test_the_gridcap_lp_has_the_lessons_size_and_optimum(gridcap_lp, exact):
    assert (len(gridcap_lp["c"]), len(gridcap_lp["row_lb"]), len(gridcap_lp["values"])) == (80, 47, 204)
    assert exact["status"] == "Optimal"
    assert exact["objective"] == pytest.approx(26587.4415, abs=1e-3)
    assert violation(gridcap_lp, exact["x"]) <= 1e-9


def test_pdlp_stops_later_and_closer_as_the_tolerance_shrinks(gridcap_lp, exact):
    runs = [ortools_pdlp(gridcap_lp, eps) for eps in (1e-2, 1e-4, 1e-6, 1e-8)]
    assert [r["iterations"] for r in runs] == sorted(r["iterations"] for r in runs)
    for eps, r in zip((1e-2, 1e-4, 1e-6, 1e-8), runs):
        assert relative_difference(r["objective"], exact["objective"]) <= eps
    assert sum(v in (0.0, 1.0) for v in runs[-1]["x"]) < sum(v in (0.0, 1.0) for v in exact["x"])


def test_switching_off_rescaling_or_restarts_costs_iterations(gridcap_lp):
    default = ortools_pdlp(gridcap_lp, 1e-6)["iterations"]
    no_restarts = ortools_pdlp(gridcap_lp, 1e-6, tweaks={
        "restart_strategy": solvers_pb2.PrimalDualHybridGradientParams.NO_RESTARTS})["iterations"]
    no_scaling = ortools_pdlp(gridcap_lp, 1e-6, tweaks={"l_inf_ruiz_iterations": 0, "l2_norm_rescaling": False},
                              iteration_limit=20_000)
    assert no_restarts > 10 * default
    assert no_scaling["status"] == "TERMINATION_REASON_ITERATION_LIMIT"


def test_the_cpu_path_agrees_with_the_reference(gridcap_lp, exact):
    result, tried = solve_lp(gridcap_lp, use_gpu=False)
    assert tried == ["highs-ipm Optimal"]
    assert agrees(result, exact, gridcap_lp)
    assert not agrees({**result, "objective": result["objective"] * (1 + 1e-5)}, exact, gridcap_lp)


def test_highspy_pdlp_is_refused_without_a_gpu(monkeypatch, gridcap_lp):
    monkeypatch.setattr(lps, "gpu_available", lambda: False)
    with pytest.raises(RuntimeError, match="only on a GPU"):
        highs(gridcap_lp, "pdlp")


def test_ortools_pdlp_matches_interior_point_on_transport():
    m = transport(30)
    ipm, pdlp = highs(m, "ipm"), ortools_pdlp(m, 1e-6)
    assert ipm["objective"] == pytest.approx(38917.0, abs=1e-3)
    assert relative_difference(pdlp["objective"], ipm["objective"]) <= 1e-6


def test_cpu_solvers_repeat_bit_for_bit_and_pdlp_threads_change_the_bits():
    m = transport(100)
    for run_once in (lambda: highs(m, "ipm"), lambda: ortools_pdlp(m, 1e-6), lambda: ortools_pdlp(m, 1e-6, threads=4)):
        a, b = run_once(), run_once()
        assert digest(a["x"]) == digest(b["x"]) and a["objective"] == b["objective"]
    assert digest(ortools_pdlp(m, 1e-6)["x"]) != digest(ortools_pdlp(m, 1e-6, threads=4)["x"])


def test_the_manifest_asks_for_equal_bits_only_from_a_repeat():
    m = transport(30)
    a = manifest(m, ortools_pdlp(m, 1e-6), "pdlp", 1e-6, 1, "cpu")
    b = manifest(m, ortools_pdlp(m, 1e-6), "pdlp", 1e-6, 1, "cpu")
    other = manifest(m, highs(m, "ipm"), "ipm", 1e-8, 1, "cpu")
    assert compare(a, b) == "identical"
    assert compare(a, other) == "within tolerance"
    b["result"]["x"] = "0" * 16
    assert compare(a, b) == "different"
    assert compare(a, manifest(transport(31), highs(transport(31), "ipm"), "ipm", 1e-8, 1, "cpu")) == "not comparable"


def test_a_race_or_a_cuopt_milp_is_never_held_to_its_bits():
    m = transport(30)
    run_ = ortools_pdlp(m, 1e-6)
    race = manifest(m, {**run_, "solver": "cuopt-lp"}, "dual simplex", 1e-4, 0, "cpu", requested="concurrent")
    again = manifest(m, {**run_, "solver": "cuopt-lp", "x": [v + 1e-9 for v in run_["x"]]}, "dual simplex", 1e-4, 0,
                     "cpu", requested="concurrent")
    assert race["solver"]["requested"] == "concurrent" and compare(race, again) == "within tolerance"
    milp, _ = gridcap_timing("small", integer=True)
    plan = highs(milp, threads=1, gap=1e-3)
    one = manifest(milp, {**plan, "solver": "cuopt-milp"}, "milp", 1e-3, 0, "cpu")
    two = manifest(milp, {**plan, "solver": "cuopt-milp", "x": plan["x"][::-1]}, "milp", 1e-3, 0, "cpu")
    assert one["inputs"]["kind"] == "milp" and compare(one, two) == "within tolerance"
    three = manifest(milp, {**plan, "x": plan["x"][::-1]}, "milp", 1e-3, 0, "cpu")    # HiGHS: bits are owed
    assert compare(manifest(milp, plan, "milp", 1e-3, 0, "cpu"), three) == "different"


def test_a_highslp_gives_the_same_answer_column_or_row_wise():
    from highs_lp import build, solve
    for colwise in (True, False):
        status, objective, x = solve(build(colwise))
        assert status == "Optimal" and objective == pytest.approx(12.0) and x == pytest.approx([2.0, 0.0, 1.0])
    status, objective, x = solve(build(True, integer=False))
    assert status == "Optimal" and abs(objective - 12.5) <= 1e-9


def test_the_milp_check_accepts_highs_plan_and_refuses_a_broken_one():
    m, _ = gridcap_timing("small", integer=True)
    r = highs(m, threads=1, gap=1e-3)
    assert check(m, r, r["bound"], 1e-3)[0]
    worse = {**r, "x": [1.0] * len(r["x"])}
    assert not check(m, worse, r["bound"], 1e-3)[0]


def test_the_policy_never_needs_a_gpu_and_keeps_the_plan_of_record_on_the_cpu():
    for job in jobs:
        assert decide(job, gpu=False).device == "cpu"
        if job.use == "plan":
            assert decide(job, gpu=True).device == "cpu" and decide(job, gpu=True).threads == 1
        if decide(job, gpu=True).device == "gpu":
            assert decide(job, gpu=True).verify_on_cpu
    assert decide(Job("tiny", "lp", 50, "bound"), gpu=True).device == "cpu"


def test_the_cuopt_worker_explains_itself_without_a_job():
    done = subprocess.run([sys.executable, str(SRC / "cuopt_worker.py")], capture_output=True, text=True)
    assert done.returncode == 0 and "cuOpt" in done.stdout


# ---------------------------------------------------------------- on the GPU variant with a GPU only
@requires_gpu()
def test_highs_gpu_pdlp_is_refused_on_the_gridcap_lp_and_the_fallback_answers(gridcap_lp, exact):
    result, tried = solve_lp(gridcap_lp)
    assert tried == ["highs-pdlp Unknown", "highs-ipm Optimal"]
    assert agrees(result, exact, gridcap_lp)


@requires_gpu()
def test_gpu_pdlp_repeats_bit_for_bit_and_agrees_across_devices_within_tolerance():
    m = transport(100)
    ipm = highs(m, "ipm")
    a, b = highs(m, "pdlp"), highs(m, "pdlp")
    assert a["status"] == "Optimal" and digest(a["x"]) == digest(b["x"])
    assert digest(a["x"]) != digest(ipm["x"])
    assert agrees(a, ipm, m)
    c, d = cuopt(m, "pdlp"), cuopt(m, "pdlp")
    assert c["solved_by"] == "1" and c["digest"] == d["digest"]
    assert relative_difference(c["objective"], ipm["objective"]) <= 1e-4


@requires_gpu()
def test_a_cuopt_milp_plan_is_checked_not_trusted():
    m, _ = gridcap_timing("small", integer=True)
    ref = highs(m, threads=1, gap=1e-3)
    r = cuopt(m, settings={"mip_relative_gap": 1e-3, "time_limit": 30}, want_x=True)
    assert check(m, r, min(ref["bound"], r["bound"]), 1e-3)[0]


@requires_gpu()
def test_the_live_policy_runs_a_large_lp_on_the_gpu():
    out = run(jobs[3], transport(300))
    assert out["policy"]["device"] == "gpu" and out["result"]["status"] == "Optimal"
