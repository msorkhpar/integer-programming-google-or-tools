from policy import Policy, decide

GPU_BOX = {"gpu": True, "cuopt": True, "cores": 16}
LAPTOP = {"gpu": False, "cuopt": False, "cores": 8}


def job(kind, nonzeros, use):
    return {"kind": kind, "nonzeros": nonzeros, "use": use}


def test_a_published_answer_runs_on_one_cpu_thread_everywhere():
    for machine in (GPU_BOX, LAPTOP):
        assert decide(job("milp", 40_000, "publish"), machine) == Policy("cpu", "highs", "branch-and-bound", 1, 1e-4, False)
        assert decide(job("lp", 3_000_000, "publish"), machine) == Policy("cpu", "highs", "simplex", 1, 1e-7, False)


def test_a_large_lp_goes_to_the_gpu_and_a_small_one_stays_on_the_cpu():
    assert decide(job("lp", 3_000_000, "bound"), GPU_BOX) == Policy("gpu", "highs", "pdlp", 1, 1e-6, True)
    assert decide(job("lp", 3_000_000, "bound"), LAPTOP) == Policy("cpu", "highs", "ipm", 4, 1e-8, False)
    assert decide(job("lp", 20_000, "explore"), GPU_BOX) == Policy("cpu", "highs", "simplex", 1, 1e-7, False)


def test_a_gpu_without_cuopt_keeps_an_exploratory_milp_on_the_cpu():
    box = {"gpu": True, "cuopt": False, "cores": 16}
    assert decide(job("milp", 40_000, "explore"), box) == Policy("cpu", "highs", "branch-and-bound", 4, 1e-2, False)
    assert decide(job("milp", 40_000, "explore"), GPU_BOX).device == "gpu"


def test_an_lp_of_exactly_the_threshold_size_is_large():
    assert decide(job("lp", 500_000, "bound"), GPU_BOX).device == "gpu"
    assert decide(job("lp", 499_999, "bound"), GPU_BOX).device == "cpu"


def test_cpu_threads_never_exceed_the_machine():
    two = {"gpu": False, "cuopt": False, "cores": 2}
    assert decide(job("milp", 40_000, "explore"), two).threads == 2
    assert decide(job("lp", 3_000_000, "explore"), two).threads == 2


def test_every_gpu_answer_is_verified():
    assert decide(job("milp", 40_000, "explore"), GPU_BOX) == Policy("gpu", "cuopt", "milp", 16, 1e-2, True)
