from __future__ import annotations


def work_to_gap(progress: list[tuple[float, float, float]], target: float) -> float | None:
    """Work at the first (work, incumbent, bound) row with |bound - incumbent| / |incumbent| <= target."""
    for work, incumbent, bound in progress:
        if abs(bound - incumbent) / abs(incumbent) <= target:
            return work
    return None


if __name__ == "__main__":
    log = [(10, 900.0, 1000.0), (25, 950.0, 1000.0), (60, 985.0, 1000.0), (90, 995.0, 1000.0)]
    print(work_to_gap(log, 0.01))
