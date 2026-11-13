from __future__ import annotations

import numpy as np

Rule = tuple[dict[int, float], str, float]


def to_leq(rules: list[Rule], n: int) -> tuple[np.ndarray, np.ndarray]:
    """Write rules over n variables as one A and one b with every row in the form a @ x <= b."""
    rows, rhs = [], []
    for coeffs, sense, limit in rules:
        row = np.zeros(n)
        for j, a in coeffs.items():
            row[j] = a
        if sense in ("<=", "=="):
            rows.append(row)
            rhs.append(limit)
        if sense in (">=", "=="):
            rows.append(-row)
            rhs.append(-limit)
    return np.array(rows).reshape(len(rows), n), np.array(rhs, dtype=float)


if __name__ == "__main__":
    A, b = to_leq([({0: 1, 1: 1}, "<=", 4), ({0: 1}, ">=", 1)], 2)
    print(A)
    print(b)
