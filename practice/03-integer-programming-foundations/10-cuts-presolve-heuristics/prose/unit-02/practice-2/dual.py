from __future__ import annotations


def dual_fixings(objective: dict[str, float],
                 rows: dict[str, tuple[dict[str, float], float]]) -> dict[str, int]:
    """The variables dual fixing sets, and the value it sets each to (maximization, <= rows)."""
    # TODO: for each variable, collect its coefficients over every row that contains it; fix it at 1
    # when its value is 0 or more and none of them is positive, at 0 when its value is negative and
    # none of them is negative.
    return {}


if __name__ == "__main__":
    print(dual_fixings({"a": 5, "b": 3, "c": 4}, {"r1": ({"a": 2, "b": 3}, 4)}))
