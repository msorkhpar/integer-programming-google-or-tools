from __future__ import annotations

from ortools.math_opt.python import mathopt


def coefficients(benefits: dict[tuple[str, int], dict[str, float]], reference: dict[str, float],
                 weights: dict[str, float]) -> dict[tuple[str, int], float]:
    """{(main, start year): value in $k of NPV-equivalent} for every row of `benefits`."""
    # TODO: one value per row, in $k of NPV-equivalent.
    out = {key: 0.0 for key in benefits}
    return out


def objective(x: dict[tuple[str, int], mathopt.Variable], coefficient: dict) -> mathopt.LinearExpression:
    """The plan's value: each start variable times its coefficient."""
    # TODO
    return mathopt.LinearExpression()


if __name__ == "__main__":
    reference = {"breaks": 4.0, "leakage": 200.0, "npv": 1_000.0}
    weights = {"breaks": 0.4, "leakage": 0.2, "npv": 0.4}
    print(coefficients({("Elm", 2028): {"breaks": 2.0, "leakage": 50.0, "npv": 300.0}}, reference, weights))
