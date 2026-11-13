from __future__ import annotations


def accept(x: list[float], reported: float, bounds: list[float], values: list[float], hours: list[list[float]],
           capacity: list[float], requires: list[tuple[int, int]], gap: float) -> tuple[bool, str]:
    """Check a selection from an untrusted MILP solver (maximise value); return (accepted, reason)."""
    if any(abs(v - round(v)) > 1e-5 for v in x):
        return False, "not integral"
    plan = [round(v) for v in x]
    for q, limit in enumerate(capacity):
        if sum(hours[j][q] * plan[j] for j in range(len(plan))) > limit + 1e-6:
            return False, f"over capacity in quarter {q + 1}"
    for a, b in requires:
        if plan[b] > plan[a]:
            return False, f"job {b} without job {a}"
    worth = sum(v * p for v, p in zip(values, plan))          # recomputed: the report is not evidence
    best = min(bounds)                                        # the tightest bound any solver proved
    if (best - worth) / abs(best) > gap:
        return False, "outside the gap"
    return True, "accepted"


if __name__ == "__main__":
    print(accept([1, 0], 5.0, [5.0], [5.0, 4.0], [[2, 0], [1, 1]], [2.0, 1.0], [(0, 1)], 1e-3))
