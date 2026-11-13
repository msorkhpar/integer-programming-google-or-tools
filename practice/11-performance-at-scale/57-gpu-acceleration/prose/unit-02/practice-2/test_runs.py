import hashlib
import struct

import highspy

from runs import check_runs


def gpu_available() -> bool:
    """The course's answer when its GPU helper is importable (the GPU image adds GPU checks); False otherwise."""
    try:
        from gpu import gpu_available as found
    except ImportError:
        return False
    return found()


def solve(method):
    """A 2 x 2 transportation LP with highspy; the run record check_runs reads."""
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("solver", method)
    inf = highspy.kHighsInf
    h.addVars(4, [0.0] * 4, [inf] * 4)
    h.changeColsCost(4, [0, 1, 2, 3], [1.0, 3.0, 2.0, 1.0])
    h.addRow(-inf, 5.0, 2, [0, 1], [1.0, 1.0])
    h.addRow(-inf, 5.0, 2, [2, 3], [1.0, 1.0])
    h.addRow(4.0, inf, 2, [0, 2], [1.0, 1.0])
    h.addRow(6.0, inf, 2, [1, 3], [1.0, 1.0])
    h.run()
    x = list(h.getSolution().col_value)
    return {"device": "gpu" if method == "pdlp" else "cpu", "solver": method,
            "objective": h.getInfo().objective_function_value,
            "digest": hashlib.sha256(struct.pack(f"<{len(x)}d", *x)).hexdigest()[:16]}


def run(device, solver, objective, digest):
    return {"device": device, "solver": solver, "objective": objective, "digest": digest}


def test_real_runs_on_this_machine_agree_and_a_run_off_by_a_thousandth_is_caught():
    runs = [solve("ipm"), solve("ipm")]
    if gpu_available():                        # on the GPU image with a GPU: the GPU's PDLP joins, twice
        runs += [solve("pdlp"), solve("pdlp")]
    assert check_runs(runs, 1e-6) == []
    assert check_runs(runs + [run("gpu", "other", runs[0]["objective"] * 1.001, "f00d")], 1e-6) == [
        "gpu/other: off the reference"]


def test_a_repeat_that_changed_is_caught():
    runs = [run("cpu", "ipm", 12.0, "aa"), run("gpu", "pdlp", 12.0000001, "bb"), run("gpu", "pdlp", 12.0000001, "cc")]
    assert check_runs(runs, 1e-6) == ["gpu/pdlp: repeat differs"]
    assert check_runs(runs[:2], 1e-6) == []


def test_different_solvers_are_not_held_to_equal_bits():
    runs = [run("cpu", "simplex", 12.0, "aa"), run("cpu", "ipm", 12.0, "bb"), run("gpu", "pdlp", 12.000001, "cc")]
    assert check_runs(runs, 1e-6) == []
    assert check_runs(runs + [run("cpu", "ipm", 12.0, "dd")], 1e-6) == ["cpu/ipm: repeat differs"]


def test_the_tolerance_is_relative_to_the_objective():
    runs = [run("cpu", "ipm", 2_000_000.0, "aa"), run("gpu", "pdlp", 2_000_001.0, "bb")]
    assert check_runs(runs, 1e-6) == []
    assert check_runs([run("cpu", "ipm", 2_000_000.0, "aa"), run("gpu", "pdlp", 2_000_010.0, "bb")], 1e-6) == [
        "gpu/pdlp: off the reference"]


def test_without_a_cpu_run_there_is_no_reference():
    runs = [run("gpu", "pdlp", 12.0, "aa"), run("gpu", "pdlp", 12.0, "aa")]
    assert check_runs(runs, 1e-6) == ["no CPU reference"]
    changed = [run("gpu", "pdlp", 12.0, "aa"), run("gpu", "pdlp", 12.5, "bb")]   # no repeat check without a CPU run
    assert check_runs(changed, 1e-6) == ["no CPU reference"]
    assert check_runs([run("cpu", "ipm", 12.0, "bb")] + runs, 1e-6) == []
