from pytest import approx

from speedup import crossover, speedups


def rec(solver, device, n, seconds, first=False, err=1e-9):
    return {"solver": solver, "device": device, "n": n, "seconds": seconds, "first_in_process": first, "rel_error": err}


def test_the_speed_up_is_the_best_cpu_time_over_the_best_gpu_time():
    records = [rec("ipm", "cpu", 1000, 12.0), rec("pdlp-cpu", "cpu", 1000, 10.0),
               rec("highs-gpu", "gpu", 1000, 2.5), rec("other-gpu", "gpu", 1000, 2.0),
               rec("ipm", "cpu", 100, 0.05), rec("highs-gpu", "gpu", 100, 0.25), rec("other-gpu", "gpu", 100, 0.2)]
    assert speedups(records, 1e-6) == {100: approx(0.25), 1000: approx(5.0)}
    assert speedups(records + [rec("highs-gpu", "gpu", 30, 0.2)], 1e-6) == {     # no CPU run at n = 30
        30: None, 100: approx(0.25), 1000: approx(5.0)}


def test_the_crossover_is_where_the_gpu_starts_winning():
    assert crossover({30: 0.03, 100: 0.2, 300: 1.7, 1000: 11.0}) == 300
    assert crossover({30: 0.03, 100: 0.2}) is None


def test_a_process_first_gpu_solve_is_left_out():
    records = [rec("ipm", "cpu", 300, 0.6), rec("highs-gpu", "gpu", 300, 0.9, first=True),
               rec("highs-gpu", "gpu", 300, 0.4)]
    assert speedups(records, 1e-6) == {300: approx(1.5)}
    inaccurate_first = rec("highs-gpu", "gpu", 300, 0.9, first=True, err=1e-3)   # left out of the accuracy check too
    assert speedups(records + [inaccurate_first], 1e-6) == {300: approx(1.5)}


def test_one_slow_repeat_does_not_set_the_time():
    records = [rec("ipm", "cpu", 300, 0.6)] + [rec("highs-gpu", "gpu", 300, s) for s in (0.3, 0.3, 3.0)]
    assert speedups(records, 1e-6) == {300: approx(2.0)}


def test_a_gpu_solver_less_accurate_than_needed_does_not_count():
    records = [rec("ipm", "cpu", 1000, 12.0), rec("highs-gpu", "gpu", 1000, 2.4, err=2e-9),
               rec("cuopt", "gpu", 1000, 1.2, err=3e-5)]
    assert speedups(records, 1e-6) == {1000: approx(5.0)}
    assert speedups([rec("ipm", "cpu", 1000, 12.0), rec("cuopt", "gpu", 1000, 1.2, err=3e-5)], 1e-6) == {1000: None}


def test_a_size_where_the_gpu_loses_again_moves_the_crossover_up():
    assert crossover({100: 1.2, 300: 0.9, 1000: 11.0}) == 1000
