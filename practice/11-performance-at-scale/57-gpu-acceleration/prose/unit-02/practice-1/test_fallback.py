import highspy

from fallback import solve_with_fallback


def gpu_available() -> bool:
    """The course's answer when its GPU helper is importable (the GPU image adds GPU checks); False otherwise."""
    try:
        from gpu import gpu_available as found
    except ImportError:
        return False
    return found()


def fake(name, needs_gpu, status=None, calls=None, raises=False):
    def solve(model):
        if calls is not None:
            calls.append(name)
        if raises:
            raise RuntimeError("out of GPU memory")
        return {"status": status, "objective": 7.0, "by": name}
    return {"name": name, "needs_gpu": needs_gpu, "solve": solve}


def test_without_a_gpu_the_gpu_solver_is_never_called():
    calls = []
    solvers = [fake("gpu-pdlp", True, "Optimal", calls), fake("cpu-ipm", False, "Optimal", calls)]
    result, log = solve_with_fallback("lp", solvers, gpu=False)
    assert calls == ["cpu-ipm"]
    assert result is not None and result["by"] == "cpu-ipm"
    assert log == ["gpu-pdlp: skipped (no GPU)", "cpu-ipm: Optimal"]


def highs_solver(name, method, needs_gpu):
    def solve(costs):
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("solver", method)
        inf = highspy.kHighsInf
        h.addVars(4, [0.0] * 4, [inf] * 4)
        h.changeColsCost(4, list(range(4)), costs)
        h.addRow(-inf, 5.0, 2, [0, 1], [1.0, 1.0])          # source 0 ships at most 5
        h.addRow(-inf, 5.0, 2, [2, 3], [1.0, 1.0])          # source 1 ships at most 5
        h.addRow(4.0, inf, 2, [0, 2], [1.0, 1.0])           # sink 0 needs 4
        h.addRow(6.0, inf, 2, [1, 3], [1.0, 1.0])           # sink 1 needs 6
        h.run()
        return {"status": h.modelStatusToString(h.getModelStatus()), "objective": h.getInfo().objective_function_value}
    return {"name": name, "needs_gpu": needs_gpu, "solve": solve}


def test_a_real_lp_is_solved_on_whatever_this_machine_has():
    gpu = gpu_available()
    solvers = [highs_solver("highs-pdlp", "pdlp", True), highs_solver("highs-ipm", "ipm", False)]
    result, log = solve_with_fallback([1.0, 3.0, 2.0, 1.0], solvers, gpu)
    assert result is not None and abs(result["objective"] - 12.0) <= 1e-6 * 12.0
    if gpu:                                     # on the GPU image with a GPU: the GPU was tried first
        assert log[0].startswith("highs-pdlp: ") and log[0] != "highs-pdlp: skipped (no GPU)"
    else:
        assert log == ["highs-pdlp: skipped (no GPU)", "highs-ipm: Optimal"]


def test_a_gpu_answer_that_is_not_optimal_falls_through():
    solvers = [fake("gpu-pdlp", True, "Unknown"), fake("cpu-ipm", False, "Optimal")]
    result, log = solve_with_fallback("lp", solvers, gpu=True)
    assert result is not None and result["by"] == "cpu-ipm"
    assert log == ["gpu-pdlp: Unknown", "cpu-ipm: Optimal"]


def test_a_solver_that_raises_is_logged_and_the_next_one_runs():
    solvers = [fake("gpu-pdlp", True, raises=True), fake("cpu-ipm", False, "Optimal")]
    result, log = solve_with_fallback("lp", solvers, gpu=True)
    assert result is not None and result["by"] == "cpu-ipm"
    assert log == ["gpu-pdlp: error", "cpu-ipm: Optimal"]


def test_when_no_solver_answers_optimal_there_is_no_result():
    solvers = [fake("gpu-pdlp", True, "Unknown"), fake("cpu-ipm", False, "Time limit reached")]
    result, log = solve_with_fallback("lp", solvers, gpu=True)
    assert result is None
    assert log == ["gpu-pdlp: Unknown", "cpu-ipm: Time limit reached"]
