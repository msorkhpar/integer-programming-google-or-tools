from __future__ import annotations

Row = tuple[dict[str, float], str, float]       # (coefficients by variable, "<=" | ">=" | "==", right-hand side)


def standard_form(variables: list[str], objective: dict[str, float], sense: str, rows: list[Row]):
    """Rewrite an LP as max c.x s.t. A x <= b, x >= 0. Returns (c, A, b) as plain lists."""
    # TODO: c for a maximization, then one or two rows of A and b per row, in the order given.
    return [], [], []

if __name__ == "__main__":
    print(standard_form(["x", "y"], {"x": 1, "y": 3}, "min", [({"x": 2, "y": -1}, ">=", 6)]))
