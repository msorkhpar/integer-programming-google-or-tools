from __future__ import annotations


def dual_fixings(objective: dict[str, float],
                 rows: dict[str, tuple[dict[str, float], float]]) -> dict[str, int]:
    """The variables dual fixing sets, and the value it sets each to (maximization, <= rows)."""
    fixed = {}
    for j, c in objective.items():
        column = [coefs[j] for coefs, _ in rows.values() if j in coefs]
        if c >= 0 and all(a <= 0 for a in column):
            fixed[j] = 1
        elif c < 0 and all(a >= 0 for a in column):
            fixed[j] = 0
    return fixed


if __name__ == "__main__":
    print(dual_fixings({"a": 5, "b": 3, "c": 4}, {"r1": ({"a": 2, "b": 3}, 4)}))
