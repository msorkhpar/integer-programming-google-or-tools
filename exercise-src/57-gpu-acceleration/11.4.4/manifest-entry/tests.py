import json

from manifest import entry

CPU = {"device": "cpu"}
GPU = {"device": "gpu", "name": "Example GPU 9000", "compute_capability": "9.0", "driver_cuda": "13.2",
       "cuda_runtime": "13.3.29", "uuid": "GPU-00000000-0000-0000-0000-000000000000"}
RESULT = {"status": "Optimal", "objective": 4_812.25, "x_digest": "9f1c", "iterations": 1_472}


def test_a_cpu_run_records_its_solver_and_its_result():
    settings = {"solver": "ortools", "method": "pdlp", "tolerance": 1e-6, "threads": 1}
    assert entry(settings, RESULT, CPU) == {
        "solver": {"name": "ortools", "method": "pdlp", "tolerance": 1e-6, "threads": 1, "device": "cpu"},
        "result": RESULT}


def test_a_gpu_run_records_the_card_model_and_cuda_but_not_its_uuid():
    settings = {"solver": "highs", "method": "pdlp", "tolerance": 1e-7, "threads": 1}
    made = entry(settings, RESULT, GPU)
    assert made.get("solver") == {"name": "highs", "method": "pdlp", "tolerance": 1e-7, "threads": 1, "device": "gpu",
                              "device_name": "Example GPU 9000", "driver_cuda": "13.2", "cuda_runtime": "13.3.29"}
    assert "GPU-0000" not in json.dumps(made)


def test_a_concurrent_run_records_the_method_that_won():
    settings = {"solver": "cuopt", "method": "concurrent", "tolerance": 1e-4, "threads": 0}
    made = entry(settings, {**RESULT, "solved_by": "dual simplex"}, GPU)
    assert made is not None and made.get("solver", {}).get("method") == "dual simplex"
    assert made["solver"].get("requested") == "concurrent"


def test_a_concurrent_run_without_its_winner_is_refused():
    settings = {"solver": "cuopt", "method": "concurrent", "tolerance": 1e-4, "threads": 0}
    assert entry(settings, RESULT, GPU) is None
    assert entry({**settings, "method": "pdlp"}, RESULT, GPU) is not None


def test_the_clock_and_the_machine_stay_out_of_the_result():
    settings = {"solver": "highs", "method": "ipm", "tolerance": 1e-8, "threads": 1}
    made = entry(settings, {**RESULT, "seconds": 0.48, "started": "2026-11-12T02:00:00", "host": "build-01"}, CPU)
    assert made.get("result") == RESULT
