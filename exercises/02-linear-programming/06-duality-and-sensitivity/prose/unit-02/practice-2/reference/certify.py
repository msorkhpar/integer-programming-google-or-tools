from __future__ import annotations

import numpy as np


def certify(value: dict[str, float], rows: dict[str, tuple[dict[str, float], str, float]],
            plan: dict[str, float], tol: float = 1e-6) -> dict[str, float] | None:
    """The prices that prove `plan` optimal, or None if complementary slackness shows it is not."""
    def activity(coeffs):
        return sum(c * plan[a] for a, c in coeffs.items())

    binding = [name for name, (coeffs, _, rhs) in rows.items() if abs(activity(coeffs) - rhs) <= tol]
    used = [a for a in value if plan[a] > tol]
    matrix = np.array([[rows[name][0].get(a, 0) for name in binding] for a in used], dtype=float)
    solved = np.linalg.solve(matrix, np.array([value[a] for a in used], dtype=float))
    prices = {name: 0.0 for name in rows}
    prices.update(zip(binding, map(float, solved)))
    for name, (_, sense, _) in rows.items():
        if (sense == "<=" and prices[name] < -tol) or (sense == ">=" and prices[name] > tol):
            return None
    for a in value:
        reduced = value[a] - sum(coeffs.get(a, 0) * prices[name] for name, (coeffs, _, _) in rows.items())
        if reduced > tol:
            return None
    return prices


if __name__ == "__main__":
    value = {"posters": 4, "flyers": 3}
    rows = {"press": ({"posters": 1, "flyers": 1}, "<=", 10), "paper": ({"posters": 1}, "<=", 6)}
    print(certify(value, rows, {"posters": 6, "flyers": 4}))
    print(certify(value, rows, {"posters": 0, "flyers": 10}))
