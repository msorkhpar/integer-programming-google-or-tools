from __future__ import annotations


def check_runs(runs: list[dict], tol: float) -> list[str]:
    """Problems with a set of runs of one LP on several devices; an empty list means they agree.

    A run is {"device": "cpu" | "gpu", "solver": str, "objective": float, "digest": str}.
    """
    # TODO: a CPU reference, repeats held to equal bits, every run within tol of the reference.
    return ["not checked"]

if __name__ == "__main__":
    print(check_runs([{"device": "cpu", "solver": "ipm", "objective": 10.0, "digest": "a"}], 1e-6))
