from __future__ import annotations

import numpy as np

Rule = tuple[dict[int, float], str, float]


def to_leq(rules: list[Rule], n: int) -> tuple[np.ndarray, np.ndarray]:
    """Write rules over n variables as one A and one b with every row in the form a @ x <= b."""
    # TODO: one or two rows per rule, depending on its sense (see the statement).
    return np.zeros((0, n)), np.zeros(0)


if __name__ == "__main__":
    A, b = to_leq([({0: 1, 1: 1}, "<=", 4), ({0: 1}, ">=", 1)], 2)
    print(A)
    print(b)
