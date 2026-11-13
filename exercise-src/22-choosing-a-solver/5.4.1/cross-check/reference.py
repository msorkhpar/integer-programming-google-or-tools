from __future__ import annotations

import statistics


def suspects(results: dict[str, tuple[str, float]], rel_tol: float) -> list[str]:
    """Names of the OPTIMAL solvers whose objective is off the OPTIMAL median by more than rel_tol * max(1, |median|)."""
    optimal = {name: z for name, (status, z) in results.items() if status == "OPTIMAL"}
    if not optimal:
        return []
    reference = statistics.median(optimal.values())
    allowed = rel_tol * max(1.0, abs(reference))
    return sorted(name for name, z in optimal.items() if abs(z - reference) > allowed)


if __name__ == "__main__":
    print(suspects({"A": ("OPTIMAL", 20.3078), "B": ("OPTIMAL", 20.3078), "C": ("OPTIMAL", 19.68)}, 1e-6))
