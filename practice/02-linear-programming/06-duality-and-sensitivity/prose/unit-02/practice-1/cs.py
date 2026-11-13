from __future__ import annotations


def cs_violations(value: dict[str, float], rows: dict[str, tuple[dict[str, float], str, float]],
                  plan: dict[str, float], prices: dict[str, float], tol: float = 1e-6) -> list[str]:
    """The rows and activities where the plan and the prices break complementary slackness, sorted."""
    # TODO: one check per row (slack and price), one per activity (value and reduced cost).
    return []


if __name__ == "__main__":
    value = {"inspect": 4, "repair": 3}
    rows = {"hours": ({"inspect": 1, "repair": 1}, "<=", 10), "inspect_cap": ({"inspect": 1}, "<=", 6)}
    print(cs_violations(value, rows, {"inspect": 6, "repair": 4}, {"hours": 3, "inspect_cap": 1}))
    print(cs_violations(value, rows, {"inspect": 5, "repair": 4}, {"hours": 3, "inspect_cap": 1}))
