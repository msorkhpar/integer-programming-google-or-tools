from __future__ import annotations

import numpy as np


def certify(value: dict[str, float], rows: dict[str, tuple[dict[str, float], str, float]],
            plan: dict[str, float], tol: float = 1e-6) -> dict[str, float] | None:
    """The prices that prove `plan` optimal, or None if complementary slackness shows it is not."""
    # TODO: price 0 on rows with slack; solve "reduced cost = 0" for the used products with
    # np.linalg.solve; then check every price's sign and every reduced cost.
    return None


if __name__ == "__main__":
    value = {"posters": 4, "flyers": 3}
    rows = {"press": ({"posters": 1, "flyers": 1}, "<=", 10), "paper": ({"posters": 1}, "<=", 6)}
    print(certify(value, rows, {"posters": 6, "flyers": 4}))
    print(certify(value, rows, {"posters": 0, "flyers": 10}))
