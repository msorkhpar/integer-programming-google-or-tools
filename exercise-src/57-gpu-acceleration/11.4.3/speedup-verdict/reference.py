from __future__ import annotations

from statistics import median


def speedups(records: list[dict], needed: float) -> dict[int, float | None]:
    """For each size n: the best CPU time over the best eligible GPU time (None if no GPU run is eligible).

    A record is {"solver", "device", "n", "seconds", "first_in_process", "rel_error"}. A solver's time is the
    median of its runs, leaving out each process's first GPU solve; a GPU solver is eligible only if every
    run it counts has rel_error within `needed`. A size with no CPU run gets None.
    """
    out = {}
    for n in sorted({r["n"] for r in records}):
        times = {"cpu": {}, "gpu": {}}
        accurate = {}
        for r in records:
            if r["n"] != n or r["first_in_process"]:
                continue
            times[r["device"]].setdefault(r["solver"], []).append(r["seconds"])
            accurate[r["solver"]] = accurate.get(r["solver"], True) and r["rel_error"] <= needed
        if not times["cpu"]:                         # no CPU run at this size: nothing to compare with
            out[n] = None
            continue
        cpu = min(median(t) for t in times["cpu"].values())
        gpu = [median(t) for s, t in times["gpu"].items() if accurate[s]]
        out[n] = cpu / min(gpu) if gpu else None
    return out


def crossover(table: dict[int, float | None]) -> int | None:
    """The smallest size from which the GPU is faster at that size and every larger one."""
    best = None
    for n in sorted(table, reverse=True):
        if table[n] is None or table[n] <= 1.0:
            break
        best = n
    return best


if __name__ == "__main__":
    rows = [{"solver": "ipm", "device": "cpu", "n": 300, "seconds": 0.6, "first_in_process": False, "rel_error": 0.0},
            {"solver": "pdlp", "device": "gpu", "n": 300, "seconds": 0.4, "first_in_process": False, "rel_error": 2e-9}]
    print(speedups(rows, 1e-6), crossover(speedups(rows, 1e-6)))
