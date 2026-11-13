from __future__ import annotations


def accept(x: list[float], reported: float, bounds: list[float], values: list[float], hours: list[list[float]],
           capacity: list[float], requires: list[tuple[int, int]], gap: float) -> tuple[bool, str]:
    """Check a selection from an untrusted MILP solver (maximise value); return (accepted, reason)."""
    # TODO: integral, within each quarter's crew-weeks, dependencies kept, and its own worth within the gap.
    return True, "accepted"


if __name__ == "__main__":
    print(accept([1, 0], 5.0, [5.0], [5.0, 4.0], [[2, 0], [1, 1]], [2.0, 1.0], [(0, 1)], 1e-3))
