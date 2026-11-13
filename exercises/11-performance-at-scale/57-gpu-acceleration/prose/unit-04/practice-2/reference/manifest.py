from __future__ import annotations

KEPT = ("status", "objective", "x_digest", "iterations")


def entry(settings: dict, result: dict, device: dict) -> dict | None:
    """The manifest's solver and result blocks for one run, or None when a concurrent run lacks its winner.

    settings: {"solver", "method", "tolerance", "threads"}; result: what the solver returned; device: where
    the solve ran, {"device": "cpu"} or a GPU report with "name", "driver_cuda", "cuda_runtime" and more.
    """
    method = settings["method"]
    if method == "concurrent":
        method = result.get("solved_by")
        if method is None:
            return None
    solver = {"name": settings["solver"], "method": method, "tolerance": settings["tolerance"],
              "threads": settings["threads"], "device": device["device"]}
    if settings["method"] == "concurrent":
        solver["requested"] = "concurrent"
    if device["device"] == "gpu":
        solver.update(device_name=device["name"], driver_cuda=device["driver_cuda"],
                      cuda_runtime=device["cuda_runtime"])
    return {"solver": solver, "result": {k: result[k] for k in KEPT if k in result}}


if __name__ == "__main__":
    print(entry({"solver": "highs", "method": "simplex", "tolerance": 1e-7, "threads": 1},
                {"status": "Optimal", "objective": 12.0, "x_digest": "ab", "iterations": 4}, {"device": "cpu"}))
