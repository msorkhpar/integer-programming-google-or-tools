from __future__ import annotations

Row = tuple[dict[str, float], str, float]       # (coefficients by variable, "<=" | ">=" | "==", right-hand side)


def standard_form(variables: list[str], objective: dict[str, float], sense: str, rows: list[Row]):
    """Rewrite an LP as max c.x s.t. A x <= b, x >= 0. Returns (c, A, b) as plain lists."""
    sign = 1.0 if sense == "max" else -1.0
    c = [sign * objective.get(v, 0.0) for v in variables]
    A, b = [], []
    for coefficients, op, rhs in rows:
        row = [coefficients.get(v, 0.0) for v in variables]
        if op in ("<=", "=="):
            A.append(row)
            b.append(rhs)
        if op in (">=", "=="):
            A.append([-a for a in row])
            b.append(-rhs)
    return c, A, b


if __name__ == "__main__":
    print(standard_form(["x", "y"], {"x": 1, "y": 3}, "min", [({"x": 2, "y": -1}, ">=", 6)]))
