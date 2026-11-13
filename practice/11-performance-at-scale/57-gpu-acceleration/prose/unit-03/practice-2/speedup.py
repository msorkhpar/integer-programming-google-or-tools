from __future__ import annotations

from statistics import median


def speedups(records: list[dict], needed: float) -> dict[int, float | None]:
    """For each size n: the best CPU time over the best eligible GPU time (None if no GPU run is eligible).

    A record is {"solver", "device", "n", "seconds", "first_in_process", "rel_error"}. A solver's time is the
    median of its runs, leaving out each process's first GPU solve; a GPU solver is eligible only if every
    run it counts has rel_error within `needed`. A size with no CPU run gets None.
    """
    # TODO: per size, the median time per solver without first GPU solves, then the best CPU over the
    # best GPU solver accurate enough.
    return {}


def crossover(table: dict[int, float | None]) -> int | None:
    """The smallest size from which the GPU is faster at that size and every larger one."""
    # TODO: walk the sizes from the largest down.
    return None


if __name__ == "__main__":
    rows = [{"solver": "ipm", "device": "cpu", "n": 300, "seconds": 0.6, "first_in_process": False, "rel_error": 0.0},
            {"solver": "pdlp", "device": "gpu", "n": 300, "seconds": 0.4, "first_in_process": False, "rel_error": 2e-9}]
    print(speedups(rows, 1e-6), crossover(speedups(rows, 1e-6)))
