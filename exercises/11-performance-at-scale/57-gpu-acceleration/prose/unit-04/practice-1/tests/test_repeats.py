from repeats import verdict


def run(**changes):
    base = {"inputs": "budget-lp-2027", "device": "cpu", "solver": "highs", "method": "simplex", "threads": 1,
            "tolerance": 1e-7, "versions": "highspy 1.14.0", "kind": "lp", "objective": 48_210.5, "digest": "a1"}
    return {**base, **changes}


def test_a_repeat_of_one_configuration_is_held_to_its_bits():
    assert verdict(run(), run(), 1e-6) == "identical"
    assert verdict(run(), run(digest="b2"), 1e-6) == "different"


def test_runs_on_different_devices_are_compared_within_the_tolerance():
    gpu = run(device="gpu", method="pdlp", objective=48_210.5000000005, digest="c3")
    assert verdict(run(), gpu, 1e-6) == "within tolerance"
    assert verdict(run(), run(inputs="budget-lp-2028"), 1e-6) == "not comparable"


def test_a_concurrent_run_is_not_held_to_its_bits():
    a = run(solver="cuopt", device="gpu", method="concurrent", digest="d4")
    b = run(solver="cuopt", device="gpu", method="concurrent", objective=48_210.51, digest="e5")
    assert verdict(a, b, 1e-6) == "within tolerance"
    assert verdict(a, run(solver="cuopt", device="gpu", method="concurrent", objective=48_250.0), 1e-6) == "different"


def test_a_cuopt_milp_is_not_held_to_its_bits():
    a = run(solver="cuopt", device="gpu", method="milp", kind="milp", objective=61_587.1, digest="f6")
    b = run(solver="cuopt", device="gpu", method="milp", kind="milp", objective=61_587.100000000006, digest="a7")
    assert verdict(a, b, 1e-6) == "within tolerance"
    assert verdict(run(kind="milp", method="milp"), run(kind="milp", method="milp", digest="b8"), 1e-6) == "different"


def test_a_different_thread_count_is_another_configuration():
    a = run(solver="ortools", method="pdlp", tolerance=1e-6, digest="c9")
    b = run(solver="ortools", method="pdlp", tolerance=1e-6, threads=4, objective=48_210.5000001, digest="d0")
    assert verdict(a, b, 1e-6) == "within tolerance"
    assert verdict(a, run(solver="ortools", method="pdlp", tolerance=1e-6, digest="e1"), 1e-6) == "different"


def test_the_tolerance_is_relative_to_the_objective():
    big = run(objective=2_000_000_000.0)
    assert verdict(big, run(device="gpu", method="pdlp", objective=2_000_001_000.0, digest="f2"), 1e-6) == "within tolerance"
    assert verdict(big, run(device="gpu", method="pdlp", objective=2_000_010_000.0, digest="f3"), 1e-6) == "different"
