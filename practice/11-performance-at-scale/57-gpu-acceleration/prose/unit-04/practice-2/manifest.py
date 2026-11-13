from __future__ import annotations

KEPT = ("status", "objective", "x_digest", "iterations")


def entry(settings: dict, result: dict, device: dict) -> dict | None:
    """The manifest's solver and result blocks for one run, or None when a concurrent run lacks its winner.

    settings: {"solver", "method", "tolerance", "threads"}; result: what the solver returned; device: where
    the solve ran, {"device": "cpu"} or a GPU report with "name", "driver_cuda", "cuda_runtime" and more.
    """
    # TODO: the solver block (with the winner of a race, and a GPU's model and CUDA versions), then the
    # result block with only the kept fields.
    return {}


if __name__ == "__main__":
    print(entry({"solver": "highs", "method": "simplex", "tolerance": 1e-7, "threads": 1},
                {"status": "Optimal", "objective": 12.0, "x_digest": "ab", "iterations": 4}, {"device": "cpu"}))
